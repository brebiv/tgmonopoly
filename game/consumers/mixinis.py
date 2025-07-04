from abc import ABC
from channels.db import database_sync_to_async

from game.models import Game
from game.serializers import GameSerializer


class AsyncORMMixin(ABC):
    @database_sync_to_async
    def get_waiting_games(self):
        return Game.objects.filter(status=Game.Status.WAITING).prefetch_related(
            "board_config"
        )

    @database_sync_to_async
    def get_waiting_games_serialized(self):
        games = Game.objects.filter(status=Game.Status.WAITING).prefetch_related(
            "board_config"
        )
        serializer = GameSerializer(games, many=True)
        return serializer.data
