from channels.generic.websocket import AsyncJsonWebsocketConsumer
from game.consumers.mixinis import AsyncORMMixin, AuthMixin


class GameListConsumer(AsyncJsonWebsocketConsumer, AsyncORMMixin, AuthMixin):
    async def connect(self):
        await self.authenticate_async()

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
        if self.scope.get("telegram_user") is not None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        pass

    async def receive(self, text_data):
        pass

    async def game_created(self, event):
        await self.send_json(event)
