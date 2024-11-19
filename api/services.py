import random
import uuid
from django.utils import timezone
from celery import current_app

from game.models import Game, Player, GameEffect, Tile, Ownership, ChanceCard, PropertyGroup
from game import config
from .types import GameActionType, GameEventType
from .tasks import handle_game_effect_timeout
from .serializers import GameEventSerializer, GameSerializer, PlayerSerializer, OwnershipSerializer


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
    def apply_effect(game: Game, player: Player, name: str, effect_data: dict = None) -> GameEffect:
        effect_timeout = config.EFFECTS_TIMEOUTS[name]

        effect_timeout_timestamp = (timezone.now() + timezone.timedelta(seconds=effect_timeout)).timestamp() * 1000
        
        effect_data = effect_data or {}
        effect_data['timeout'] = effect_timeout_timestamp
        effect_data['created'] = timezone.now().timestamp() * 1000

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
    def assemble_game_frame(game: Game, events: list, type = 'game.action') -> dict:
        events_serializer = GameEventSerializer(data=events, many=True)

        if not events_serializer.is_valid():
            raise Exception("Invalid events", events_serializer.errors)

        ownerships = Ownership.objects.filter(game=game)
        ownerships_serializer = OwnershipSerializer(ownerships, many=True)

        return {
            'type': type,
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
    def roll_dice(game: Game, player: Player) -> list:
        events = []
        dices = [random.randint(1, 6) for _ in range(2)]
        # dices = [10, 10]

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
                    # Should be placed in next_turn or something
                    game.turn += 1
                    game.current_player = GameService.calculate_next_player(game, player)
                    GameService.calculate_mortages(game, player)

                    GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
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

            # Should be placed in next_turn or something
            next_player = GameService.calculate_next_player(game, player)
            if next_player:
                game.current_player = next_player
                game.turn += 1
                game.save()
                GameService.calculate_mortages(game, player)
                GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
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

                next_player = GameService.calculate_next_player(game, player)
                if next_player:
                    game.current_player = next_player
                    game.turn += 1
                    game.save()
                    GameService.calculate_mortages(game, player)
                    GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
            elif card.card_type == ChanceCard.GO_TO_JAIL:
                player.position = Tile.objects.get(type=Tile.JAIL).position
                player.in_jail = True
                player.jail_turns = 0
                player.save()

                next_player = GameService.calculate_next_player(game, player)
                if next_player:
                    game.current_player = next_player
                    game.turn += 1
                    game.save()
                    GameService.calculate_mortages(game, player)
                    GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
            elif card.card_type == ChanceCard.MONEY_TO_PLAYER:
                from_player = card.details.get('from')
                amount = card.details.get('amount')
                if from_player == 'all':
                    from_players = game.players.exclude(id=player.id)
                    total_recieved = 0
                    for sender in from_players:
                        payment = min(sender.cash, amount)
                        print(payment)
                        sender.cash -= payment
                        sender.save()
                        total_recieved += payment
                    player.cash += total_recieved
                    player.save()
                
                next_player = GameService.calculate_next_player(game, player)
                if next_player:
                    game.current_player = next_player
                    game.turn += 1
                    game.save()
                    GameService.calculate_mortages(game, player)
                    GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
            elif card.card_type == ChanceCard.MONEY:
                player.cash += card.details.get('amount')
                player.save()

                next_player = GameService.calculate_next_player(game, player)
                if next_player:
                    game.current_player = next_player
                    game.turn += 1
                    game.save()
                    GameService.calculate_mortages(game, player)
                    GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
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
            # Should be placed in next_turn or something
            game.turn += 1
            game.current_player = GameService.calculate_next_player(game, player)
            GameService.calculate_mortages(game, player)

            GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

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
            next_player = GameService.calculate_next_player(game, player)
            if next_player:
                game.current_player = next_player
                game.turn += 1
                game.save()
                GameService.calculate_mortages(game, player)
                GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
        
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
                # effect = GameEffect.objects.create(
                #     game=game,
                #     player=player,
                #     name=GameEffect.ROLL_DICE,
                # )
                game.turn += 1
                game.current_player = GameService.calculate_next_player(game, player)
                game.save()
                GameService.calculate_mortages(game, player)

                GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
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
        # effect = GameEffect.objects.create(
        #     game=game,
        #     player=player,
        #     name=GameEffect.ROLL_DICE,
        # )
        game.turn += 1
        game.current_player = GameService.calculate_next_player(game, player)
        game.save()
        GameService.calculate_mortages(game, player)

        GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

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

        next_player = GameService.calculate_next_player(game, player)
        if next_player:
            game.current_player = next_player
            game.turn += 1
            game.save()
            GameService.calculate_mortages(game, player)
            
            GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

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

        next_player = GameService.calculate_next_player(game, player)
        if next_player:
            game.current_player = next_player
            game.turn += 1
            game.save()
            GameService.calculate_mortages(game, player)
            GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

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

        next_player = GameService.calculate_next_player(game, player)
        if next_player:
            game.current_player = next_player
            game.turn += 1
            game.save()
            GameService.calculate_mortages(game, player)
            GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

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
        next_player = GameService.calculate_next_player(game, player)
        if next_player:
            game.current_player = next_player
            game.turn += 1
            game.save()
            GameService.calculate_mortages(game, player)
            GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

        return events
