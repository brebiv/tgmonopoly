import random
import uuid
from django.utils import timezone
from django.db.models import QuerySet, Q
from django.conf import settings
from celery import current_app

from game.models import (
    Game, Player, GameEffect, Tile, Ownership, 
    ChanceCard, PropertyGroup, Property
)
from game import config
from game.exceptions import GameException
from game.tasks import handle_game_effect_timeout
from api.types import GameActionType, GameEventType, TradeData, AuctionData, WSEventType
from api.serializers import GameEventSerializer, GameSerializer, PlayerSerializer, OwnershipSerializer
from api.utils import is_running_tests

class GameService:

    ROUND_TRIP_BONUS = 200

    @staticmethod
    def calculate_next_player(game: Game, after_player: Player) -> Player:
        game_players: list[Player] = game.players.filter(status=Player.PLAYING).order_by('created')

        if game_players.count() == 0:
            game.status = Game.FINISHED
            game.save()
            return None
        # elif game_players.count() == 1:
        #     game.status = Game.FINISHED
        #     game.save()
        #     game_players[0].status = Player.WON
        #     game_players[0].save()
        #     return None

        current_index = next((index for index, p in enumerate(game_players) if p == after_player), -1)
        next_index = (current_index + 1) % len(game_players)

        next_player = game_players[next_index]

        if next_player.status == Player.LOST or next_player.status == Player.TIMEOUT:
            return GameService.calculate_next_player(game, next_player)

        return game_players[next_index]

    @staticmethod
    def apply_effect(game: Game, player: Player, name: str, effect_data: dict = None, timeout: int = None) -> GameEffect:
        if timeout:
            effect_timeout = timeout
        else:
            effect_timeout = config.EFFECTS_TIMEOUTS[name]

        # For some reason it becomes 3000 sec
        if settings.DEVELOPMENT and effect_timeout <= 0:
            effect_timeout = 10
        
        effect_timeout_timestamp = (timezone.now() + timezone.timedelta(seconds=effect_timeout)).timestamp() * 1000
        
        effect_data = effect_data or {}
        effect_data['timeout'] = effect_timeout_timestamp
        effect_data['created'] = timezone.now().timestamp() * 1000
        effect_data['trade_count'] = effect_data.get('trade_count', 0)
        effect_data['trade_accepted'] = effect_data.get('trade_accepted', False)

        task_id = str(uuid.uuid4())

        effect = GameEffect.objects.create(
            game=game,
            player=player,
            name=name,
            effect_data=effect_data,
            task_id=task_id
        )

        if not config.DISABLE_AFK:
            handle_game_effect_timeout.apply_async(
                (effect.pk,), 
                countdown=effect_timeout, 
                task_id=task_id
            )

        return effect

    @staticmethod
    def remove_effect(game: Game, player: Player, name: str) -> GameEffect:
        effect = GameEffect.objects.filter(player=player, name=name).last()
        if effect:
            if not config.DISABLE_AFK:
                if effect.task_id:
                    current_app.control.revoke(effect.task_id)
            effect.delete()

        return effect
    
    @staticmethod
    def next_turn(game: Game, after_player: Player) -> list[dict]:
        events = []

        next_player = GameService.calculate_next_player(game, after_player)

        if next_player:
            game.current_player = next_player
            game.turn += 1
            game.save()
            GameService.calculate_mortages(game, next_player)
            GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

            events.append({
                'type': 'game.service',
                'action': GameEventType.NEXT_TURN,
            })
    
    @staticmethod
    def assemble_game_frame(game: Game, events: list, type = WSEventType.GAME_ACTION) -> dict:
        events_serializer = GameEventSerializer(data=events, many=True)

        if not events_serializer.is_valid():
            raise Exception("Invalid events", events_serializer.errors)

        ownerships = Ownership.objects.filter(game=game)
        ownerships_serializer = OwnershipSerializer(ownerships, many=True)

        return {
            'type': type.value,
            'game': GameSerializer(game).data,
            'players': [PlayerSerializer(player).data for player in game.players.all()],
            'events': events_serializer.data,
            'ownerships': ownerships_serializer.data
        }

    @staticmethod
    def start_game(game: Game, player: Player) -> list:
        events = []

        GameService.apply_effect(game, player, GameEffect.ROLL_DICE)

        game.players.update(status=Player.PLAYING)

        game.turn += 1
        game.current_player = player
        game.status = Game.PLAYING
        game.save()

        return [{
            'type': 'game.action',
            'action': GameActionType.START_GAME,
            'player': player.pk,
        },]
    
    @staticmethod
    def roll_dice(game: Game, player: Player, override_dices: list[int] | None = None) -> list:
        events = []

        # if override_dices:
        #     dices = override_dices
        if is_running_tests():
            dices = config.TEST_DICE_VALUES
        else:
            dices = [random.randint(1, 6) for _ in range(2)]

        events.append({
            'type': 'game.action',
            'action': GameEventType.ROLL_DICE,
            'player': player.pk,
            'dices': dices,
        })

        GameService.remove_effect(game, player, GameEffect.ROLL_DICE)

        if player.in_jail:
            events.extend(GameService._handle_jail_roll(game, player, dices))
        else:
            events.extend(GameService._handle_normal_roll(game, player, dices))

        return events
    
    @staticmethod
    def _handle_normal_roll(game: Game, player: Player, dice_values: list[int]) -> list[dict]:
        events = []
        dice_sum = sum(dice_values)
        passed_start = player.position + dice_sum >= 40

        if player.move_backwards:
            new_postion = player.move_backward(dice_sum)
            player.move_backwards = False
            player.save()
        else:
            new_postion = player.move_forward(dice_sum)

        events.append({
            'type': 'game.action',
            'action': GameEventType.MOVE_PLAYER,
            'player': player.pk,
            'position': player.position,
        })

        if passed_start:
            events.append({
                'type': 'game.action',
                'action': GameEventType.PASSED_START,
                'player': player.pk,
                'amount': GameService.ROUND_TRIP_BONUS,
            })
            player.cash += GameService.ROUND_TRIP_BONUS
            player.save()

        tile = Tile.objects.get(position=new_postion)
        if tile.type == Tile.PROPERTY:
            try:
                ownership = Ownership.objects.get(game=game, property=tile.property)
            except Ownership.DoesNotExist:
                GameService.apply_effect(game, player, GameEffect.ASK_BUY, {
                    'price': tile.property.price,
                })
            else:
                if ownership.player == player:
                    events.append({
                        'type': 'game.action',
                        'action': GameEventType.STEPPED_ON_OWN_PROPERTY,
                        'player': player.pk,
                        'tile': tile.pk,
                    })

                    GameService.next_turn(game, player)
                else:
                    rent = 0
                    if ownership.property.group.name == PropertyGroup.UTILITIES_1:
                        rent = ownership.calculate_rent()
                    else:
                        # rent = ownership.calculate_rent(dice_sum=Dice.objects.filter(game=game).count())
                        rent = ownership.calculate_rent(dice_sum=dice_sum)

                    GameService.apply_effect(game, player, GameEffect.PAY_RENT, {
                        'rent': rent,
                    })
        elif tile.type == Tile.JAIL or tile.type == Tile.POLICE:
            if tile.type == Tile.POLICE:
                jail_position = Tile.objects.get(type=Tile.JAIL).position
                player.position = jail_position
                events.append({
                    'type': 'game.action',
                    'action': GameEventType.MOVE_PLAYER,
                    'player': player.pk,
                    'position': player.position,
                })
            player.in_jail = True
            player.save()

            events.append({
                'type': 'game.action',
                'action': GameEventType.GO_TO_PRISON,
                'player': player.pk,
            })

            GameService.next_turn(game, player)
        elif tile.type == Tile.CHANCE:
            card = ChanceCard.get_random_card()
            # card = ChanceCard.objects.filter(card_type=ChanceCard.MOVE_BACKWARDS).first()

            events.append({
                'type': 'game.action',
                'action': GameEventType.CHANCE_CARD,
                'player': player.pk,
                'chance_card_data': {
                    'title': card.title,
                    'description': card.description,
                    'card_type': card.card_type,
                    'details': card.details,
                }
            })

            if card.card_type == ChanceCard.MOVE_BACKWARDS:
                player.move_backwards = True
                player.save()
                GameService.next_turn(game, player)
            elif card.card_type == ChanceCard.GO_TO_JAIL:
                player.position = Tile.objects.get(type=Tile.JAIL).position
                player.in_jail = True
                player.jail_turns = 0
                player.save()

                GameService.next_turn(game, player)
            elif card.card_type == ChanceCard.MONEY_TO_PLAYER:
                from_player = card.details.get('from')
                amount = card.details.get('amount')
                if from_player == 'all':
                    from_players = game.players.exclude(id=player.id)
                    total_recieved = 0
                    for sender in from_players:
                        payment = min(sender.cash, amount)
                        sender.cash -= payment
                        sender.save()
                        total_recieved += payment
                    player.cash += total_recieved
                    player.save()
                
                GameService.next_turn(game, player)
            elif card.card_type == ChanceCard.MONEY:
                player.cash += card.details.get('amount')
                player.save()
                GameService.next_turn(game, player)
            elif card.card_type == ChanceCard.REPAIRS:
                house_repair_cost = card.details.get('house_repair_cost')
                houses_owned = player.houses_owned()
                repair_cost = house_repair_cost * houses_owned

                GameService.apply_effect(game, player, GameEffect.PAY_REPAIRS, {
                    'repair_cost': repair_cost,
                    'number_of_houses': houses_owned,
                    'house_repair_cost': house_repair_cost,
                })
        elif tile.type == Tile.CASINO:
            events.append({
                'type': 'game.action',
                'action': GameEventType.GO_TO_CASINO,
                'player': player.pk,
            })

            available_bets = [10, 20, 30, 40, 50]

            GameService.apply_effect(game, player, GameEffect.IN_CASINO, {
                'available_bets': available_bets,
            })

            # # Should be placed in next_turn or something
            # next_player = GameService.calculate_next_player(game, player)
            # if next_player:
            #     game.current_player = next_player
            #     game.turn += 1
            #     game.save()
            #     GameService.calculate_mortages(game, player)
            #     GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
        else:
            GameService.next_turn(game, player)

        game.save()
        player.save()

        return events

    @staticmethod
    def _handle_jail_roll(game: Game, player: Player, dice_values: list[int]) -> list[dict]:
        events = []
        
        if dice_values[0] == dice_values[1]:
            player.in_jail = False
            player.jail_turns = 0
            player.save()

            events.append({
                'type': 'game.action',
                'action': GameEventType.RELEASE_FROM_PRISON,
                'player': player.pk,
            })
            GameService.apply_effect(game, player, GameEffect.ROLL_DICE)
        else:
            player.jail_turns += 1
            player.save()
            events.append({
                'type': 'game.action',
                'action': GameEventType.PRISON_RELEASE_FAIL,
                'player': player.pk,
                'tries_left': config.MAXIMUM_JAIL_TURNS - player.jail_turns,
            })

            GameService.next_turn(game, player)
        
        return events
    
    @staticmethod
    def buy_property(game: Game, player: Player) -> list:
        events = []
        tile = Tile.objects.get(position=player.position)

        if tile.type == Tile.PROPERTY:
            try:
                ownership = Ownership.objects.get(player=player, property=tile.property)
                if ownership.player == player:
                    raise Exception("You already own this property")
                else:
                    raise Exception("You are not the owner of this property")
            except Ownership.DoesNotExist:
                ownership = Ownership.objects.create(
                    game=game,
                    player=player,
                    property=tile.property,
                )
                player.cash -= tile.property.price
                player.save()
                
                tile.property.owner = player
                tile.property.save()

                GameService.remove_effect(game, player, GameEffect.ASK_BUY)

                events.append({
                    'type': 'game.action',
                    'action': GameEventType.BUY_PROPERTY,
                    'player': player.pk,
                    'tile': tile.pk,
                })

                # If double add roll dice effect to current player else to the next one
                GameService.next_turn(game, player)
        return events
    
    @staticmethod
    def pay_rent(game: Game, player: Player) -> list:
        events = []
        tile = Tile.objects.get(position=player.position)

        if tile.type != Tile.PROPERTY:
            raise Exception("You can't pay rent on a non-property tile")

        
        pay_rent_effect = GameEffect.objects.filter(player=player, name=GameEffect.PAY_RENT).last()
        ownership = Ownership.objects.get(game=game, property=tile.property)

        rent_price = pay_rent_effect.effect_data['rent']

        if rent_price > player.cash:
            raise Exception("You don't have enough cash to pay rent")
            

        player.cash -= rent_price
        player.save()
        ownership.player.cash += rent_price
        ownership.player.save()

        GameService.remove_effect(game, player, GameEffect.PAY_RENT)

        events.append({
            'type': 'game.action',
            'action': GameEventType.PAY_RENT,
            'player': player.pk,
            'amount': rent_price,
            'to_player': ownership.player.pk,
        })

        # If double add roll dice effect to current player else to the next one
        GameService.next_turn(game, player)

        return events
    
    @staticmethod
    def handle_afk(game: Game, player: Player, effect: GameEffect) -> list:
        events = []

        effect.delete()
        player.status = Player.TIMEOUT
        player.save()

        events.append({
            'type': 'game.action',
            'action': GameEventType.TIMEOUT,
            'player': player.pk,
        })

        GameService.next_turn(game, player)

        return events
    
    @staticmethod
    def pay_for_prison(game: Game, player: Player) -> list[dict]:
        events = []

        if player.cash < config.PRISON_PAY_AMOUNT:
            raise Exception("You don't have enough cash to pay for prison")
        
        GameService.remove_effect(game, player, GameEffect.ROLL_DICE)

        player.in_jail = False
        player.jail_turns = 0
        player.cash -= config.PRISON_PAY_AMOUNT
        player.save()

        events.append({
            'type': 'game.action',
            'action': GameEventType.PAY_FOR_PRISON,
            'player': player.pk,
        })

        GameService.apply_effect(game, player, GameEffect.ROLL_DICE)

        return events
    
    @staticmethod
    def calculate_mortages(game: Game, player: Player) -> list[dict]:
        events = []

        for ownership in Ownership.objects.filter(player=player, mortgaged=True):
            if ownership.mortage_last_turn:
                if game.turn >= ownership.mortage_last_turn:
                    ownership.delete()
                    # ownership.mortgaged = False
                    # ownership.mortage_last_turn = None
                    # ownership.save()
                    events.append({
                        'type': 'game.action',
                        'action': 'MORTAGE_EXPIRED',
                        'player': player.pk,
                        'property_id': ownership.property.pk,
                    })

        return events
    
    @staticmethod
    def mortage_property(game: Game, player: Player, property_id: int) -> list[dict]:
        events = []

        try:
            ownership = Ownership.objects.get(player=player, property_id=property_id)
        except Ownership.DoesNotExist:
            raise Exception("You don't own this property")

        ownership.mortgaged = True
        ownership.mortage_last_turn = game.turn + config.MORTAGE_MAX_TURNS
        ownership.save()

        player.cash += ownership.property.mortgage_value
        player.save()

        events.append({
            'type': 'game.action',
            'action': GameEventType.MORTAGE_PROPERTY,
            'player': player.pk,
            'tile': ownership.property.board_space.position,
        })

        return events

    @staticmethod
    def buyouy_property(game: Game, player: Player, property_id: int) -> list[dict]:
        events = []

        try:
            ownership = Ownership.objects.get(player=player, property_id=property_id)
        except Ownership.DoesNotExist:
            raise Exception("You don't own this property")

        ownership.mortgaged = False
        ownership.mortage_last_turn = 0
        ownership.save()

        player.cash -= ownership.property.buyout_price
        player.save()

        events.append({
            'type': 'game.action',
            'action': GameEventType.BUYOUT_PROPERTY,
            'player': player.pk,
            'tile': ownership.property.board_space.position,
        })

        return events
    
    @staticmethod
    def buy_house(game: Game, player: Player, property_id: int):
        events = []

        try:
            ownership = Ownership.objects.get(player=player, property_id=property_id)
            property = ownership.property
        except Ownership.DoesNotExist:
            raise Exception("You don't own this property")
        
        can_build, message = ownership.can_build_house()
        if not can_build:
            raise Exception(message)
        

        ownership.houses += 1
        ownership.save()
        player.cash -= property.house_price
        player.save()

        last_effect = GameEffect.objects.filter(player=player).last()
        last_effect.effect_data['bought_house'] = True
        last_effect.save()

        events.append({
            'type': 'game.action',
            'action': GameEventType.BUY_HOUSE,
            'player': player.pk,
            'tile': property.board_space.position,
        })

        return events
    
    @staticmethod
    def sell_house(game: Game, player: Player, property_id: int):
        events = []

        try:
            ownership = Ownership.objects.get(player=player, property_id=property_id)
            property = ownership.property
        except Ownership.DoesNotExist:
            raise Exception("You don't own this property")
        
        can_build, message = ownership.can_sell_house()
        if not can_build:
            raise Exception(message)

        ownership.houses -= 1
        ownership.save()
        player.cash += property.house_price
        player.save()

        events.append({
            'type': 'game.action',
            'action': GameEventType.SELL_HOUSE,
            'player': player.pk,
            'tile': property.board_space.position,
        })

        return events
    
    @staticmethod
    def pay_to_bank(game: Game, player: Player, amount: int) -> list[dict]:
        events = []

        if player.cash < amount:
            raise Exception("You don't have enough cash to pay")

        GameService.remove_effect(game, player, GameEffect.PAY_REPAIRS)

        player.cash -= amount
        player.save()

        events.append({
            'type': 'game.action',
            'action': GameEventType.PAY_TO_BANK,
            'player': player.pk,
            'amount': amount,
        })

        GameService.next_turn(game, player)

        return events
    
    @staticmethod
    def reject_casino(game: Game, player: Player) -> list[dict]:
        events = []

        GameService.remove_effect(game, player, GameEffect.IN_CASINO)

        events.append({
            'type': 'game.action',
            'action': GameEventType.REJECT_CASINO,
            'player': player.pk,
        })

        GameService.next_turn(game, player)

        return events
    
    @staticmethod
    def play_casino(game: Game, player: Player, bet: int) -> list[dict]:
        events = []

        effect = GameEffect.objects.filter(player=player, name=GameEffect.IN_CASINO).last()

        if bet not in effect.effect_data['available_bets']:
            raise Exception("You can't bet that much")

        GameService.remove_effect(game, player, GameEffect.IN_CASINO)

        flip_result = random.choice([True, False])

        if flip_result:
            events.append({
                'type': 'game.action',
                'action': GameEventType.WON_CASINO,
                'player': player.pk,
                'amount': bet,
            })
            player.cash += bet
        else:
            events.append({
                'type': 'game.action',
                'action': GameEventType.LOST_CASINO,
                'player': player.pk,
                'amount': bet,
            })
            player.cash -= bet

        player.save()

        # Check if not double
        GameService.next_turn(game, player)
        return events
    
    @staticmethod
    def create_trade(game: Game, player: Player, trade_data: TradeData) -> list[dict]:
        events = []

        if not trade_data.is_valid():
            raise GameException("Invalid trade data")
        
        current_effect = player.get_current_effect()
        current_effect_data = current_effect.effect_data

        if current_effect_data['trade_count'] >= config.MAX_TRADE_PROPOSALS:
            raise GameException(f"You can't create more than {config.MAX_TRADE_PROPOSALS} trades in one turn")
        if current_effect_data.get('trade_accepted', False):
            raise GameException("You can't create more trades in this turn")

        from_player = Player.objects.get(pk=trade_data.from_player)
        to_player = Player.objects.get(pk=trade_data.to_player)

        if from_player.cash < trade_data.cash_given:
            raise GameException("You are giving more money than you have")
        
        if to_player.cash < trade_data.cash_received:
            raise GameException("Other player doesn't have enough money to send")

        removed_effect = GameService.remove_effect(game, player, GameEffect.ROLL_DICE)

        removed_effect_timeout = removed_effect.effect_data.get('timeout')

        time_left = (removed_effect_timeout - (timezone.now().timestamp() * 1000)) / 1000
        
        # for player in (from_player, to_player):
        #     GameService.apply_effect(game, player, GameEffect.IN_TRADE, {
        #         'from_player': player.pk,
        #         'to_player': player.pk,
        #         'cash_given': trade_data.cash_given,
        #         'cash_received': trade_data.cash_received,
        #         'ownerships': [o.pk for o in trade_data.ownerships],
        #         'turn_time_left': time_left,
        #     })x

        game.current_player = to_player
        game.save()

        GameService.apply_effect(game, to_player, GameEffect.IN_TRADE, {
            'from_player': from_player.pk,
            'to_player': to_player.pk,
            'cash_given': trade_data.cash_given,
            'cash_received': trade_data.cash_received,
            'ownerships': [o.pk for o in trade_data.ownerships],
            'turn_time_left': time_left,
            'trade_count': removed_effect.effect_data.get('trade_count', 0) + 1,
            'trade_accepted': False
        })

        events.append({
            'type': 'game.action',
            'action': GameEventType.CREATE_TRADE,
            'player': player.pk,
            'to_player': to_player.pk,
        })
        
        return events

    @staticmethod
    def reject_trade(game: Game, player: Player) -> list[dict]:
        events = []

        removed_trade_effect = GameService.remove_effect(game, player, GameEffect.IN_TRADE)
        from_player_id = removed_trade_effect.effect_data.get('from_player')
        turn_time_left = removed_trade_effect.effect_data.get('turn_time_left')

        from_player = Player.objects.get(pk=from_player_id)

        game.current_player = from_player
        game.save()

        effect_data = {
            "trade_count": removed_trade_effect.effect_data.get('trade_count')
        }

        GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE, 
                                 timeout=turn_time_left, effect_data=effect_data)

        events.append({
            'type': 'game.action',
            'action': GameEventType.REJECT_TRADE,
            'player': player.pk,
            'from_player': from_player.pk,
        })

        return events
    
    @staticmethod
    def accept_trade(game: Game, player: Player) -> list[dict]:
        events = []

        removed_trade_effect = GameService.remove_effect(game, player, GameEffect.IN_TRADE)
        
        trade_data = TradeData.from_dict(removed_trade_effect.effect_data)

        if not trade_data.is_valid():
            raise Exception("Invalid trade data")

        from_player_id = trade_data.from_player
        to_player_id = trade_data.to_player

        from_player = Player.objects.get(pk=from_player_id)
        to_player = Player.objects.get(pk=to_player_id)

        # Giving money from trade creator
        from_player.cash -= trade_data.cash_given
        to_player.cash += trade_data.cash_given

        # Giving what trade creator asked for
        from_player.cash += trade_data.cash_received
        to_player.cash -= trade_data.cash_received

        # Dealing with properties
        for ownership in trade_data.ownerships:
            if ownership.player == from_player:
                ownership.player = to_player
            else:
                ownership.player = from_player
            ownership.save()

        from_player.save()
        to_player.save()

        game.current_player = from_player
        game.save()

        effect_data = {
            "trade_count": removed_trade_effect.effect_data['trade_count'], 
            "trade_accepted": True
        }

        GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE, effect_data=effect_data)

        events.append({
            'type': 'game.action',
            'action': GameEventType.ACCEPT_TRADE,
            'player': player.pk,
            'from_player': from_player.pk,
        })

        return events
    
    @staticmethod
    def start_auction(game: Game, player: Player) -> list[dict]:
        events = []

        try:
            property: Property = Tile.objects.get(position=player.position).property
        except Tile.DoesNotExist:
            raise Exception("You can't start auction on a non-property tile")
        
        players_participating_in_auction: QuerySet[Player] = (
            game.players.order_by('pk')
            .exclude(pk=player.pk)
            .exclude(cash__lt=property.price)
            .exclude(in_jail=True)
            .exclude(~Q(status=Player.PLAYING))
        )

        if players_participating_in_auction.count() == 0:
            # Passing auction because there are no players participating
            raise Exception("There are no players participating in auction")
        
        GameService.remove_effect(game, player, GameEffect.ASK_BUY)

        next_player_in_auction = players_participating_in_auction.first()

        game.current_player = next_player_in_auction
        game.save()

        GameService.apply_effect(
            game,
            game.current_player,
            GameEffect.IN_AUCTION,
            {
                'started_by': player.pk,
                'current_player_in_auction': next_player_in_auction.pk,
                'players_participating_in_auction': [player.pk for player in players_participating_in_auction],
                'current_auction_price': property.price + config.AUCTION_STEP,
                # 'auction_step': config.AUCTION_STEP, 
                'property': property.pk,
            }
        )

        events.append({
            'type': 'game.action',
            'action': GameEventType.START_AUCTION,
            'player': player.pk,
        })

        return events
    
    @staticmethod
    def reject_auction(game: Game, player: Player) -> list[dict]:
        events = []

        removed_effect = GameService.remove_effect(game, player, GameEffect.IN_AUCTION)

        # started_by: int = removed_effect.effect_data.get('started_by')
        # current_player_in_auction: int = removed_effect.effect_data.get('current_player_in_auction')
        # players_participating_in_auction: list[int] = removed_effect.effect_data.get('players_participating_in_auction')
        # current_auction_price: int = removed_effect.effect_data.get('current_auction_price')
        # property: int = removed_effect.effect_data.get('property')

        auction_data = AuctionData.from_dict(removed_effect.effect_data)
        auction_data.reject()

        events.append({
            'type': 'game.action',
            'action': GameEventType.REJECT_AUCTION,
            'player': player.pk,
        })

        if auction_data.resolved:
            if auction_data.is_bet:
                auction_winner = Player.objects.get(pk=auction_data.winner)

                ownership = Ownership.objects.create(
                    game=game,
                    player=auction_winner,
                    property_id=auction_data.property,
                )

                auction_winner.cash -= auction_data.current_auction_price
                auction_winner.save()

                events.append({
                    'type': 'game.action',
                    'action': GameEventType.WON_AUCTION,
                    'player': auction_winner.pk,
                    'auction_data': auction_data.to_dict()
                })

                started_by = Player.objects.get(pk=auction_data.started_by)
                GameService.next_turn(game, started_by)
            else:
                # if player has double
                started_by = Player.objects.get(pk=auction_data.started_by)
                GameService.next_turn(game, started_by)
        else:
            # next_index = (current_player_in_auction_index + 1) % len(players_participating_in_auction)
            # next_player_id = players_participating_in_auction[next_index]

            # players_participating_in_auction.pop(current_player_in_auction_index)

            next_player = Player.objects.get(pk=auction_data.current_player_in_auction)

            game.current_player = next_player
            game.save()

            GameService.apply_effect(
                game,
                game.current_player,
                GameEffect.IN_AUCTION,
                {
                    'started_by': auction_data.started_by,
                    'current_player_in_auction': auction_data.current_player_in_auction,
                    'players_participating_in_auction': auction_data.players_participating_in_auction,
                    'current_auction_price': auction_data.current_auction_price,
                    'property': auction_data.property,
                }
            )

        return events
    
    @staticmethod
    def accept_auction(game: Game, player: Player):
        events = []

        current_effect = player.get_current_effect()
        auction_data = AuctionData.from_dict(current_effect.effect_data)

        if player.cash < auction_data.current_auction_price:
            # raise GameException(GameExceptionCode.NOT_ENOUGH_MONEY)
            raise GameException('Not enough money to accept auction')

        removed_effect = GameService.remove_effect(game, player, GameEffect.IN_AUCTION)

        auction_data.accept()

        events.append({
            'type': 'game.action',
            'action': GameEventType.ACCEPT_AUCTION,
            'player': player.pk,
            'auction_data': auction_data.to_dict()
        })

        if auction_data.resolved:
            ownership = Ownership.objects.create(
                game=game,
                player=player,
                property_id=auction_data.property,
            )

            player.cash -= auction_data.current_auction_price
            player.save()

            events.append({
                'type': 'game.action',
                'action': GameEventType.WON_AUCTION,
                'player': player.pk,
                'auction_data': auction_data.to_dict()
            })

            started_by = Player.objects.get(pk=auction_data.started_by)
            GameService.next_turn(game, started_by)
        else:
            game.current_player = Player.objects.get(pk=auction_data.current_player_in_auction)
            game.save()

            GameService.apply_effect(
                game,
                game.current_player,
                GameEffect.IN_AUCTION,
                auction_data.to_dict()
            )

        return events
