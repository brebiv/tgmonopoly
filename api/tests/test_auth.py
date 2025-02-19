from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TestCase, Client
from django.urls import reverse
from asgiref.sync import sync_to_async
import uuid
import re

from tgmonopoly.asgi import application as tgmonopoly_application
from bot.models import TelegramUser
from game.models import Game, Player, GameEffect
from game import config
from api.tests import data as test_data
from api.types import WSEventType
from api.utils import parse_user_from_qs
from api.serializers import GameSerializer, PlayerSerializer
from .utils import BaseAPITestCase


class AuthTest(TestCase):
    def setUp(self):        
        self.client = Client()
    
    def test_parse_user_from_qs_no_user(self):
        with self.assertRaises(TelegramUser.DoesNotExist):
            user = parse_user_from_qs(test_data.TELEGRAM_TEST_USER_1_WEBAPP_DATA)

    def test_parse_user_from_qs_correct(self):
        tg_user = TelegramUser.objects.create(**test_data.TG_USER_1_DICT)
        user = parse_user_from_qs(test_data.TELEGRAM_TEST_USER_1_WEBAPP_DATA)

        self.assertEqual(user, tg_user)
        self.assertEqual(user.user_id, tg_user.user_id)

    def test_correct_auth_with_new_user(self):
        url = reverse('me')

        for i, test_webapp_data in enumerate(test_data.TELEGRAM_TEST_WEBAPP_DATAS):
            headers = {
                'Authorization': f'twa {test_webapp_data}'
            }

            user_count = TelegramUser.objects.count()

            self.assertEqual(user_count, i)

            response = self.client.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)
            
            user_count = TelegramUser.objects.count()
            self.assertEqual(user_count, i+1)

            resp_data = response.json()

            user = parse_user_from_qs(test_webapp_data)

            self.assertEqual(resp_data['id'], user.user_id)
            self.assertEqual(resp_data['first_name'], user.first_name)
            self.assertEqual(resp_data['username'], user.username)
    
    def test_auth_with_existing_user(self):
        for i, test_user_dict in enumerate(test_data.TG_USER_DICTS):
            tg_user = TelegramUser.objects.create(**test_user_dict)
            user_count = TelegramUser.objects.count()

            self.assertEqual(user_count, i+1)

            url = reverse('me')
            headers = {
                'Authorization': f'twa {test_data.TELEGRAM_TEST_WEBAPP_DATAS[i]}'
            }

            response = self.client.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)

            self.assertEqual(user_count, i+1)
            
            resp_data = response.json()

            self.assertEqual(resp_data['id'], tg_user.user_id)
            self.assertEqual(resp_data['first_name'], tg_user.first_name)
            self.assertEqual(resp_data['username'], tg_user.username)
    
    def test_auth_forbidden(self):
        url = reverse('me')
        
        # Without auth header
        headers = {
        }

        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, 403)

        # With wrong auth header
        headers = {
            'Authorization': f'twa random_data'
        }
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, 403)
    
    def test_api_access_forbidden(self):
        url = reverse('create_game')
        headers = {
            'Authorization': f'twa random-data'
        }
        payload = {
            'max_players': 2
        }

        games_count = Game.objects.count()
        self.assertEqual(games_count, 0)

        response = self.client.post(url, headers=headers, data=payload)
        self.assertEqual(response.status_code, 403)

        games_count = Game.objects.count()
        self.assertEqual(games_count, 0)
    
    def test_api_access_allowed(self):
        url = reverse('create_game')
        headers = {
            'Authorization': f'twa {test_data.TELEGRAM_TEST_WEBAPP_DATAS[0]}'
        }
        payload = {
            'max_players': 2
        }

        response = self.client.post(url, headers=headers, data=payload)
        self.assertEqual(response.status_code, 200)


class WebSocketAuthTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        
        self._create_game(2)

        self.player_1, self.player_2 = self.players

        self._start_game()
        self._refresh_game_and_players()

    @database_sync_to_async
    def get_game_by_uuid(self, game_uuid: uuid.UUID) -> Game:
        return Game.objects.get(uuid=game_uuid)

    @database_sync_to_async
    def get_player_by_id(self, player_id: int) -> Player:
        return Player.objects.get(pk=player_id)

    @database_sync_to_async
    def get_current_player(self) -> Player:
        return self.game.current_player

    async def test_auth_forbidden_no_query_id(self):
        # ws_url = f"/ws/game/{self.game.uuid}/?query_id="
        ws_url = f"/ws/game/{self.game.uuid}/"
        communicator = WebsocketCommunicator(tgmonopoly_application, ws_url)
        connected, subprotocol = await communicator.connect()

        self.assertFalse(connected)
        # self.assertEqual(subprotocol, "tgmonopoly")

        # message = await communicator.receive_from()
        # print("message", message)

    async def test_auth_forbidden_wrong_values(self):
        wrong_hash_data = re.sub(r'(&hash=)[a-fA-F0-9]+', r'\112345', test_data.TELEGRAM_TEST_WEBAPP_DATAS[1])
        ws_url = f"/ws/game/{self.game.uuid}/?{wrong_hash_data}"

        communicator = WebsocketCommunicator(tgmonopoly_application, ws_url)
        connected, subprotocol = await communicator.connect()

        self.assertFalse(connected)

    async def test_game_not_found(self):
        random_uuid = str(uuid.uuid4())
        ws_url = f"/ws/game/{random_uuid}/?{test_data.TELEGRAM_TEST_WEBAPP_DATAS[0]}"

        communicator = WebsocketCommunicator(tgmonopoly_application, ws_url)
        connected, subprotocol = await communicator.connect()

        self.assertFalse(connected)
    
    async def test_auth_success(self):
        communicator = self._get_ws_communicator(self.player_1)
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)
        message = await communicator.receive_json_from()

        self.assertEqual(WSEventType(message['type']), WSEventType.GAME_CONNECTED)

        is_valid = await sync_to_async(lambda: GameSerializer(data=message['game']).is_valid())()
        if not is_valid:
            serializer = GameSerializer(data=message['game'])
            errors = await sync_to_async(lambda: serializer.errors)()
            raise Exception(errors)
        
        game_data = GameSerializer(data=message['game']).initial_data
        self.assertEqual(game_data['uuid'], str(self.game.uuid))
        self.assertEqual(game_data['max_players'], self.game.max_players)
        self.assertEqual(game_data['turn'], 1)
        self.assertEqual(game_data['current_player'], self.player_1.pk)
        self.assertEqual(game_data['status'], Game.PLAYING)

        players_data = message['players']

        players = [PlayerSerializer(data=player).initial_data for player in players_data]
        current_player = await self.get_current_player()

        for i, player in enumerate(players):
            self.assertEqual(player['id'], self.players[i].pk)
            self.assertEqual(player['position'], 0)
            self.assertEqual(player['cash'], config.STARTING_CASH)
            self.assertEqual(player['color'], self.players[i].color)
            self.assertEqual(player['in_jail'], False)
            self.assertEqual(player['jail_turns'], 0)
            if player['id'] == current_player.pk:
                self.assertEqual(len(player['effects']), 1)
                self.assertEqual(player['effects'][0]['name'], GameEffect.ROLL_DICE)
            else:
                self.assertEqual(player['effects'], [])
            self.assertEqual(player['status'], Player.PLAYING)
            self.assertEqual(player['move_backwards'], False)
