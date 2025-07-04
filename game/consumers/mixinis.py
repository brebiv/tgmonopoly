from abc import ABC
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection

from game.models import Game
from game.serializers import GameSerializer
from game.auth import TelegramWebAppAuthentication
from game.utils import update_or_create_telegram_user


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


class AuthMixin(ABC):
    def authenticate(self):
        init_data_raw = self.scope.get("query_string", None)
        if not init_data_raw:
            raise DenyConnection()

        init_data = init_data_raw.decode()

        data_is_valid, validated_data = (
            TelegramWebAppAuthentication().verify_telegram_init_data(init_data)
        )

        if not data_is_valid:
            raise DenyConnection()

        tg_user_data = validated_data.get("user")
        tg_user = update_or_create_telegram_user(tg_user_data)
        self.scope["telegram_user"] = tg_user

    @database_sync_to_async
    def authenticate_async(self):
        init_data_raw = self.scope.get("query_string", None)
        if not init_data_raw:
            raise DenyConnection()

        init_data = init_data_raw.decode()

        data_is_valid, validated_data = (
            TelegramWebAppAuthentication().verify_telegram_init_data(init_data)
        )

        if not data_is_valid:
            raise DenyConnection()

        tg_user_data = validated_data.get("user")
        tg_user = update_or_create_telegram_user(tg_user_data)
        self.scope["telegram_user"] = tg_user
