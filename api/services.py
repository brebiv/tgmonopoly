from game.models import Game, Player, GameEffect
from .serializers import GameSerializer, PlayerSerializer
from .types import GameActionType


class GameService:

    @staticmethod
    def start_game(game: Game, player: Player): 
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

        return {
            'type': 'game.action',
            'action': GameActionType.START_GAME,
            'game': GameSerializer(game).data,
            'players': [PlayerSerializer(player).data for player in game.players.all()],
            'events': [],
        }