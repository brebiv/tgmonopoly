import random
import uuid
from django.utils import timezone
from celery import current_app

from game.models import Game, Player, GameEffect, Tile, Ownership
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
            if effect.task_id:
                current_app.control.revoke(effect.task_id)
            effect.delete()

        return effect
    
    @staticmethod
    def assemble_game_frame(game: Game, events: list, type = 'game.action') -> dict:
        events_serializer = GameEventSerializer(data=events, many=True)

        if not events_serializer.is_valid():
            raise Exception("Invalid events")

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
        # dices = [random.randint(1, 6) for _ in range(2)]
        dices = [1, 2]
        dice_sum = sum(dices)

        events.append({
            'type': 'game.action',
            'action': GameEventType.ROLL_DICE,
            'player': player.pk,
            'dices': dices,
        })

        # effect = GameEffect.objects.filter(player=player, name=GameEffect.ROLL_DICE).last()
        # effect.delete()

        GameService.remove_effect(game, player, GameEffect.ROLL_DICE)

        if player.in_jail:
            pass
        else:
            passed_start = player.position + dice_sum >= 40
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
                })
                player.cash += GameService.ROUND_TRIP_BONUS
                player.save()

            tile = Tile.objects.get(position=new_postion)
            if tile.type == Tile.PROPERTY:
                try:
                    ownership = Ownership.objects.get(game=game, property=tile.property)
                except Ownership.DoesNotExist:
                    # effect = GameEffect.objects.create(
                    #     game=game,
                    #     player=player,
                    #     name=GameEffect.ASK_BUY,
                    #     effect_data={
                    #         'price': tile.property.price,
                    #     },
                    # )

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
                        game.turn += 1
                        game.current_player = GameService.calculate_next_player(game, player)

                        # effect = GameEffect.objects.create(
                        #     game=game,
                        #     player=game.current_player,
                        #     name=GameEffect.ROLL_DICE,
                        # )
                        GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
                    else:
                        # effect = GameEffect.objects.create(
                        #     game=game,
                        #     player=player,
                        #     name=GameEffect.PAY_RENT,
                        #     effect_data={
                        #         'rent': ownership.calculate_rent(),
                        #     },
                        # )
                        GameService.apply_effect(game, player, GameEffect.PAY_RENT, {
                            'rent': ownership.calculate_rent(),
                        })
            else:
                game.turn += 1
                game.current_player = GameService.calculate_next_player(game, player)

                # effect = GameEffect.objects.create(
                #     game=game,
                #     player=game.current_player,
                #     name=GameEffect.ROLL_DICE,
                # )
                GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

            game.save()
            player.save()

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

                # effect = GameEffect.objects.filter(player=player, name=GameEffect.ASK_BUY).last()
                # effect.delete()

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


                # effect = GameEffect.objects.create(
                #     game=game,
                #     player=game.current_player,
                #     name=GameEffect.ROLL_DICE,
                # )
                GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)
        return events
    
    @staticmethod
    def pay_rent(game: Game, player: Player) -> list:
        events = []
        tile = Tile.objects.get(position=player.position)

        if tile.type != Tile.PROPERTY:
            raise Exception("You can't pay rent on a non-property tile")
        
        ownership = Ownership.objects.get(game=game, property=tile.property)
        rent_price = ownership.calculate_rent()

        if rent_price > player.cash:
            raise Exception("You don't have enough cash to pay rent")

        player.cash -= rent_price
        player.save()
        ownership.player.cash += rent_price
        ownership.player.save()

        # effect = GameEffect.objects.filter(player=player, name=GameEffect.PAY_RENT).last()
        # effect.delete()

        GameService.remove_effect(game, player, GameEffect.PAY_RENT)

        events.append({
            'type': 'game.action',
            'action': GameEventType.PAY_RENT,
            'player': player.pk,
            'rent_price': rent_price,
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

        # effect = GameEffect.objects.create(
        #     game=game,
        #     player=game.current_player,
        #     name=GameEffect.ROLL_DICE,
        # )

        GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

        return events
    
    @staticmethod
    def handle_afk(game: Game, player: Player, effect: GameEffect) -> list:
        events = []

        effect.delete()
        player.status = Player.TIMEOUT
        player.save()

        next_player = GameService.calculate_next_player(game, player)
        if next_player:
            game.current_player = next_player
            game.save()
            GameService.apply_effect(game, game.current_player, GameEffect.ROLL_DICE)

        return events
