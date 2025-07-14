from uuid import uuid4
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from channels.testing import WebsocketCommunicator

from tgmonopoly.asgi import application
from . import test_data
from .mixins import TelegramAuthMixin
from bot.models import TelegramUser
from game.models import Game, BoardConfig, Player
from game.management.commands.populate_database import (
    Command as PopulateDatabaseCommand,
)


# Create your tests here.
class ApiAuthTest(TestCase, TelegramAuthMixin):
    def setUp(self):
        self.client = Client()

    def assertUserCount(self, count: int):
        user_count = TelegramUser.objects.count()
        self.assertEqual(user_count, count)

    def test_correct_auth_with_new_user(self):
        url = reverse("me")

        for i, test_webapp_data in enumerate(test_data.TG_INIT_DATA_RAW_LIST):
            headers = self.generate_auth_headers(test_webapp_data)
            self.assertUserCount(i)

            resp = self.client.get(url, headers=headers)
            self.assertEqual(resp.status_code, 200)

            resp_data = resp.json()
            resp_data_user = resp_data["user"]
            user_dict = test_data.TG_INIT_DATA_USER[i]

            self.assertUserCount(i + 1)
            self.assertEqual(resp_data_user["user_id"], user_dict["id"])
            self.assertEqual(resp_data_user["first_name"], user_dict["first_name"])

    @override_settings(TG_UPDATE_USER_ON_EACH_REQUEST=True)
    def test_auth_with_existing_user(self):
        url = reverse("me")
        created_users = test_data.create_telegram_users(limit=1)
        user_count = len(created_users)
        updated_user = created_users[0]

        updated_user.first_name = "test"
        updated_user.save()

        headers = self.generate_auth_headers(test_data.TG_INIT_DATA_RAW_LIST[0])
        self.assertUserCount(user_count)

        resp = self.client.get(url, headers=headers)
        self.assertEqual(resp.status_code, 200)

        # check that no new user was created
        self.assertUserCount(user_count)

        # check that existing user updated
        self.assertEqual(updated_user.first_name, "test")
        updated_user.refresh_from_db()
        self.assertEqual(updated_user.first_name, test_data.TG_INIT_DATA_USER[0]["first_name"])

    def test_auth_forbidden(self):
        url = reverse("me")

        resp = self.client.get(url, headers={})
        self.assertEqual(resp.status_code, 403)

        headers = self.generate_auth_headers("random_data")
        resp = self.client.get(url, headers=headers)
        self.assertEqual(resp.status_code, 403)


class WebSocketAuthTest(TestCase):
    def setUp(self):
        PopulateDatabaseCommand().populate()

        board_config = BoardConfig.objects.get()
        game = Game.objects.create(board_config=board_config)
        created_users = test_data.create_telegram_users(limit=1)
        player = Player.objects.create(game=game, user=created_users[0])

        self.game = game

    async def test_game_list_auth_forbidden(self):
        ws_url = "/ws/games/"
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertFalse(connected)

    async def test_game_list_auth_forbidden_wrong_data(self):
        ws_url = "/ws/games/?query_id=124124"
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertFalse(connected)

    async def test_game_list_auth_success(self):
        ws_url = "/ws/games/?" + test_data.TG_INIT_DATA_RAW_LIST[0]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        message = await communicator.receive_json_from()
        games = message["games"]

        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["uuid"], str(self.game.uuid))

    async def test_game_detail_auth_forbidden(self):
        ws_url = "/ws/game/412414214214/?query_id=test"
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertFalse(connected)

    async def test_game_detail_auth_success(self):
        ws_url = f"/ws/game/{self.game.uuid}/?" + test_data.TG_INIT_DATA_RAW_LIST[0]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        message = await communicator.receive_json_from()
        self.assertIsNotNone(message.get("type"))
        self.assertEqual(message.get("type"), "game.initial")
        self.assertIsNotNone(message.get("game"))
        self.assertIsNotNone(message.get("players"))
        self.assertIsNotNone(message.get("events"))

    async def test_game_detail_invalid_uuid(self):
        ws_url = "/ws/game/uuid/?" + test_data.TG_INIT_DATA_RAW_LIST[0]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_game_detail_not_found(self):
        uuid = uuid4()
        ws_url = f"/ws/game/{uuid}/?" + test_data.TG_INIT_DATA_RAW_LIST[0]
        communicator = WebsocketCommunicator(application, ws_url)
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
