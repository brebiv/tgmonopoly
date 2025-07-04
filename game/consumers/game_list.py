from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from game.auth import TelegramWebAppAuthentication
from game.utils import update_or_create_telegram_user
from game.consumers.mixinis import AsyncORMMixin


class GameListConsumer(AsyncJsonWebsocketConsumer, AsyncORMMixin):
    async def connect(self):
        # Verifying Telegram auth
        init_data_raw = self.scope.get("query_string", None)
        if not init_data_raw:
            await self.close()
            return

        init_data = init_data_raw.decode()

        data_is_valid, validated_data = (
            TelegramWebAppAuthentication().verify_telegram_init_data(init_data)
        )

        if not data_is_valid:
            await self.close()
            return

        tg_user_data = validated_data.get("user")
        tg_user = await database_sync_to_async(update_or_create_telegram_user)(
            tg_user_data
        )
        self.scope["telegram_user"] = tg_user
        self.scope["auth_completed"] = True

        self.group_name = "game_list"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        games = await self.get_waiting_games_serialized()
        games_data = {"games": games}
        await self.send_json(games_data)
        # await self.send(self.group_name)
        # await self.send(self.channel_name)
        # await self.send(str(self.groups))

    async def disconnect(self, code):
        pass

    async def receive_json(self, content):
        pass

    async def receive(self, text_data):
        pass

    async def game_created(self, event):
        await self.send_json(event)
