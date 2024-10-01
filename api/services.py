import random

from game.models import Game, Player, GameEffect
from .serializers import GameSerializer, PlayerSerializer
from .types import GameActionType


class GameService:

    @staticmethod
    def start_game(game: Game, player: Player) -> list:
        events = []
        effect = GameEffect.objects.create(
            game=game,
            user=player,
            name=GameEffect.ROLL_DICE,
            description="Players start the game",
        )

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
        dice_sum = sum(dices)

        events.append({
            'type': 'game.action',
            'action': GameActionType.ROLL_DICE,
            'player': player.pk,
            'dices': dices,
        })


        new_postion = player.move_forward(dice_sum)

        events.append({
            'type': 'game.action',
            'action': GameActionType.MOVE_PLAYER,
            'player': player.pk,
            'position': player.position,
        })

        player.save()
        return events
