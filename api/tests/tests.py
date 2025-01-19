from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TestCase, Client
from django.http import HttpResponse
from django.urls import reverse
from asgiref.sync import sync_to_async
import unittest
from unittest.mock import patch
import uuid
import re

from tgmonopoly.asgi import application as tgmonopoly_application
from bot.models import TelegramUser
from game.models import Game, Player, GameEffect, Property, Ownership
from game import config
from api.tests import data as test_data
from api.types import GameActionType, AuctionData, WSEventType, GameEventType
from api.utils import parse_user_from_qs
from api.serializers import GameActionSerializer, GameSerializer, PlayerSerializer
from api import services


# Create your tests here.
class BaseAPITestCase(TestCase):
    game: Game
    client_1: Client
    client_2: Client
    client_3: Client
    tg_user_1: TelegramUser
    tg_user_2: TelegramUser
    tg_user_3: TelegramUser
    num_players: int
    clients: list[Client]
    users: list[TelegramUser]
    players: list[Player]

    def setUp(self):
        test_data.load_all_data()

        headers_1 = {
            'Authorization': f'twa {test_data.TELEGRAM_TEST_WEBAPP_DATAS[0]}'
        }
        headers_2 = {
            'Authorization': f'twa {test_data.TELEGRAM_TEST_WEBAPP_DATAS[1]}'
        }
        headers_3 = {
            'Authorization': f'twa {test_data.TELEGRAM_TEST_WEBAPP_DATAS[2]}'
        }

        self.client_1 = Client(headers=headers_1)
        self.client_2 = Client(headers=headers_2)
        self.client_3 = Client(headers=headers_3)

        self.clients = [self.client_1, self.client_2, self.client_3]

        self.tg_user_1 = TelegramUser.objects.create(**test_data.TG_USER_1_DICT)
        self.tg_user_2 = TelegramUser.objects.create(**test_data.TG_USER_2_DICT)
        self.tg_user_3 = TelegramUser.objects.create(**test_data.TG_USER_3_DICT)

        self.users = [self.tg_user_1, self.tg_user_2, self.tg_user_3]
        self.players: list[Player] = []
    
    def _create_game(self, num_players: 2 | 3):
        if num_players != 2 and num_players != 3:
            raise ValueError("num_players must be 2 or 3")
        
        self.num_players = num_players
        
        response = self.client_1.post(
            reverse('create_game'),
            data={
                'max_players': num_players
            }
        )

        self.assertEqual(response.status_code, 200)

        resp_data = response.json()
        game_uuid = resp_data['game_uuid']

        self.game = Game.objects.get(uuid=game_uuid)
        self.players = []

        for i in range(self.num_players - 1):
            response = self.clients[i + 1].post(
                reverse('join_game'),
                data={
                    'game_uuid': game_uuid
                }
            )

            self.assertEqual(response.status_code, 200)

        self.players = list(self.game.players.all())
    
    def _start_game(self):
        response = self.client_1.post(
            reverse('game_action'),
            data={
                'action': GameActionType.START_GAME,
                'game_uuid': self.game.uuid,
            }
        )
        self.assertEqual(response.status_code, 200)

    def _start_game_and_begin_auction_flow(self):
        """
        Helper method that encapsulates the logic of:
         1) Starting the game
         2) Attempting to start an auction from start tile (which should fail)
         3) Rolling dice
         4) Attempting to start an auction from the correct tile
        """
        # 1) Start the game
        self._start_game()

        # 2) Attempt to start an auction from the start tile
        response = self.client_1.post(
            reverse('game_action'),
            data={
                'action': GameActionType.START_AUCTION,
                'game_uuid': self.game.uuid,
            }
        )
        self.assertEqual(response.status_code, 400)  # Expecting failure
        self.assertEqual(response.json()['error'], 'Unknown action')

        # 3) Roll dice
        response = self.client_1.post(
            reverse('game_action'),
            data={
                'action': GameActionType.ROLL_DICE,
                'game_uuid': self.game.uuid,
            }
        )
        self.assertEqual(response.status_code, 200)

        # 4) Now actually start an auction
        response = self.client_1.post(
            reverse('game_action'),
            data={
                'action': GameActionType.START_AUCTION,
                'game_uuid': self.game.uuid,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        # player_1, player_2 = sorted([player_1, player_2], key=lambda x: x.user.id)
        player_1, player_2, *_ = self.players

        # Testing effect data
        current_effect_2 = player_2.get_current_effect()
        effect_data = current_effect_2.effect_data

        # Effect data:
        # {
        #     'started_by': 1,
        #     'current_player_in_auction': 2,
        #     'players_participating_in_auction': [2, 3],
        #     'current_auction_price': 70,
        #     'property': 2,
        #     'timeout': 1735506491836.9802,
        #     'created': 1735506471836.984
        # }
        started_by = effect_data['started_by']
        current_player_in_auction = effect_data['current_player_in_auction']
        players_participating_in_auction = effect_data['players_participating_in_auction']
        property = Property.objects.get(pk=effect_data['property'])

        self.assertNotEqual(self.game.current_player, player_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_AUCTION)
        self.assertEqual(started_by, player_1.pk)
        self.assertEqual(current_player_in_auction, player_2.pk)
        self.assertEqual(len(players_participating_in_auction), self.num_players - 1)
        self.assertNotIn(player_1.pk, players_participating_in_auction)
        self.assertEqual(current_effect_2.effect_data['current_auction_price'], property.price + config.AUCTION_STEP)

        return response

    def _refresh_game_and_players(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    @database_sync_to_async
    def _refresh_game_and_players_async(self):
        """Refresh game and all players from DB"""
        self.game.refresh_from_db()
        for player in self.players:
            player.refresh_from_db()

    def _post_game_action(
            self,
            client: Client,
            action: GameActionType,
            expected_status_code=200,
            expected_status='ok',
            expected_error: str | None = None,
            extra_data: dict | None = None,
            enable_logging: bool = False,
            disable_asserts: bool = False,
        ) -> HttpResponse:

        payload = {
            'action': action,
            'game_uuid': self.game.uuid,
        }

        if extra_data:
            payload['extra_data'] = extra_data

        serializer = GameActionSerializer(data=payload)

        if not serializer.is_valid():
            raise Exception(serializer.errors)
        
        response = client.post(reverse('game_action'), data=serializer.data, content_type='application/json')

        if enable_logging:
            print(f"Post game action: {action} {response.content}")

        resp_data = response.json()

        if not disable_asserts:
            self.assertEqual(response.status_code, expected_status_code)
            self.assertEqual(resp_data['status'], expected_status)
            if expected_error:
                self.assertEqual(resp_data['error'], expected_error)
            else:
                with self.assertRaises(KeyError):
                    resp_data['error']

        return response

    @database_sync_to_async
    def _post_game_action_async(
            self,
            client: Client,
            action: GameActionType,
            expected_status_code=200,
            expected_status='ok',
            expected_error: str | None = None,
            extra_data: dict | None = None,
            enable_logging: bool = False,
            disable_asserts: bool = False,
        ) -> HttpResponse:

        payload = {
            'action': action,
            'game_uuid': self.game.uuid,
        }

        if extra_data:
            payload['extra_data'] = extra_data

        serializer = GameActionSerializer(data=payload)

        if not serializer.is_valid():
            raise Exception(serializer.errors)
        
        response = client.post(reverse('game_action'), data=serializer.data, content_type='application/json')

        if enable_logging:
            print(f"Post game action: {action} {response.content}")

        resp_data = response.json()

        if not disable_asserts:
            self.assertEqual(response.status_code, expected_status_code)
            self.assertEqual(resp_data['status'], expected_status)
            if expected_error:
                self.assertEqual(resp_data['error'], expected_error)
            else:
                with self.assertRaises(KeyError):
                    resp_data['error']

        return response

    def _get_ws_communicator(self, player: Player) -> WebsocketCommunicator: 
        player_index = self.players.index(player)

        ws_url = f"/ws/game/{self.game.uuid}/?{test_data.TELEGRAM_TEST_WEBAPP_DATAS[player_index]}"
        return WebsocketCommunicator(tgmonopoly_application, ws_url)


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


class GameLobbyTest(TestCase):
    def setUp(self):        
        self.client = Client()
        self.tg_user_1 = TelegramUser.objects.create(**test_data.TG_USER_1_DICT)
        self.tg_user_2 = TelegramUser.objects.create(**test_data.TG_USER_2_DICT)
    
    def test_game_create(self):
        url = reverse('create_game')
        headers = {
            'Authorization': f'twa {test_data.TELEGRAM_TEST_WEBAPP_DATAS[0]}'
        }
        payload = {
            'max_players': 2
        }

        games_count = Game.objects.count()
        self.assertEqual(games_count, 0)

        response = self.client.post(url, headers=headers, data=payload)
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()

        games_count = Game.objects.count()
        self.assertEqual(games_count, 1)

        game = Game.objects.get(uuid=resp_data['next_url'].split('/')[-1])

        self.assertEqual(resp_data['status'], 'ok')
        self.assertEqual(resp_data['next_url'], f'/game/{game.uuid}')

class AuctionAPITest(BaseAPITestCase):
    def test_create_auction_2_players(self):
        self._create_game(2)
        self._start_game_and_begin_auction_flow()

    def test_create_auction_3_players(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()
    
    def test_reject_auction_2_players(self):
        self._create_game(2)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2 = self.players

        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.REJECT)

        self._refresh_game_and_players()
        current_effect_2 = player_2.get_current_effect()

        self.assertEqual(self.game.current_player, player_2)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)

    def test_reject_auction_3_players(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2, player_3 = self.players

        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.REJECT)

        self._refresh_game_and_players()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.current_player.pk, player_3.pk)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)

        self._post_game_action(self.client_3, GameActionType.REJECT)

        self._refresh_game_and_players()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.current_player.pk, player_2.pk)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertIsNone(current_effect_3)

    def test_auction_2_players(self):
        self._create_game(2)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2 = self.players

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price = auction_data.current_auction_price

        self.assertEqual(auction_price, auction_data_raw['current_auction_price'])

        cash_before_winning = player_2.cash
        game_turn_before_winning = self.game.turn


        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()

        self.assertEqual(self.game.turn, game_turn_before_winning + 1)
        self.assertEqual(self.game.current_player, player_2)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertEqual(player_1.owned_properties.count(), 0)
        self.assertEqual(player_2.owned_properties.count(), 1)
        self.assertEqual(player_2.cash, cash_before_winning - auction_price)

    def test_auction_3_players_2_turns(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2, player_3 = self.players

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_1 = auction_data.current_auction_price

        cash_before_winning = player_3.cash
        game_turn_before_winning = self.game.turn


        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_3.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_2 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_3)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)
        self.assertEqual(auction_price_2, auction_price_1 + config.AUCTION_STEP)

        # Testing if it's not your turn
        self._post_game_action(self.client_2, GameActionType.ACCEPT, 400, "!ok", "Unknown action or it's not your turn")

        # Continuing
        self._post_game_action(self.client_3, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_3 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_2)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_AUCTION)
        self.assertIsNone(current_effect_3)
        self.assertEqual(auction_price_3, auction_price_2 + config.AUCTION_STEP)

        self._post_game_action(self.client_2, GameActionType.REJECT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.turn, game_turn_before_winning + 1)
        self.assertEqual(self.game.current_player, player_2)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_3)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertEqual(player_1.owned_properties.count(), 0)
        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_3.owned_properties.count(), 1)
        self.assertGreaterEqual(player_2.cash, 0)
        self.assertEqual(player_3.cash, cash_before_winning - auction_price_3)

    def test_auction_3_players_3_turns(self):
        self._create_game(3)
        self._start_game_and_begin_auction_flow()

        self.game.refresh_from_db()
        player_1, player_2, player_3 = self.players

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_1 = auction_data.current_auction_price

        cash_before_winning = player_2.cash
        game_turn_before_winning = self.game.turn


        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_3.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_2 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_3)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)
        self.assertEqual(auction_price_2, auction_price_1 + config.AUCTION_STEP)

        # Testing if it's not your turn
        self._post_game_action(self.client_2, GameActionType.ACCEPT, 400, "!ok", "Unknown action or it's not your turn")

        # Continuing
        self._post_game_action(self.client_3, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_2.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_3 = auction_data.current_auction_price

        self.assertEqual(self.game.current_player, player_2)
        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_AUCTION)
        self.assertIsNone(current_effect_3)
        self.assertEqual(auction_price_3, auction_price_2 + config.AUCTION_STEP)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        auction_data_raw = current_effect_3.effect_data
        auction_data = AuctionData.from_dict(auction_data_raw)
        auction_price_4 = auction_data.current_auction_price

        self.assertEqual(self.game.turn, game_turn_before_winning)
        self.assertEqual(self.game.current_player, player_3)
        self.assertIsNone(current_effect_1)
        self.assertIsNone(current_effect_2)
        self.assertEqual(current_effect_3.name, GameEffect.IN_AUCTION)
        self.assertEqual(auction_price_4, auction_price_3 + config.AUCTION_STEP)

        # Last turn
        self._post_game_action(self.client_3, GameActionType.REJECT)
        self._refresh_game_and_players()

        current_effect_1 = player_1.get_current_effect()
        current_effect_2 = player_2.get_current_effect()
        current_effect_3 = player_3.get_current_effect()

        self.assertEqual(self.game.turn, game_turn_before_winning + 1)
        self.assertEqual(self.game.current_player, player_2)
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.ROLL_DICE)
        self.assertIsNone(current_effect_3)
        self.assertEqual(player_1.owned_properties.count(), 0)
        self.assertEqual(player_2.owned_properties.count(), 1)
        self.assertEqual(player_3.owned_properties.count(), 0)
        self.assertGreaterEqual(player_2.cash, 0)
        self.assertEqual(player_2.cash, cash_before_winning - auction_price_4)

    def test_not_enough_money_for_auction(self):
        self._create_game(num_players=2)
        self._start_game_and_begin_auction_flow()

        self._refresh_game_and_players()
        player_1, player_2 = self.players

        player_2.cash = 60
        player_2.save()

        self.assertEqual(player_2.owned_properties.count(), 0)
        self.assertEqual(player_2, self.game.current_player)

        self._post_game_action(self.client_2, GameActionType.ACCEPT, 400, "!ok", "Not enough money to accept auction")

    @unittest.skip("Not implemented")
    def test_reject_auction_with_double(self):
        pass


class TradingAPITest(BaseAPITestCase):
    enable_logging: bool

    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2)

        self.player_1_ownership = Ownership.objects.create(
            game=self.game,
            player=self.players[0],
            property=Property.objects.get(board_space__position=1),
        )

        self._start_game()
        self._refresh_game_and_players()

    def _start_trade(
            self,
            from_player: Player,
            to_player: Player,
            cash_given: int = 0,
            cash_received: int = 0,
            ownerships: list[int] = [],
        ) -> HttpResponse:
        
        response = self._post_game_action(
            self.client_1,
            GameActionType.CREATE_TRADE,
            extra_data={
                "from_player": from_player.pk,
                "to_player": to_player.pk,
                "cash_given": cash_given,
                "cash_received": cash_received,
                "ownerships": ownerships
            },
            disable_asserts=True,
            enable_logging=self.enable_logging
        )

        return response

    def _start_trade_and_other_player_rejects(self, disable_assertions: bool = False) -> list[HttpResponse]:
        responses = []
        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=200,
            cash_received=100,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )
        responses.append(response)

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        if not disable_assertions:
            self.assertEqual(self.game.current_player, self.players[1])
            self.assertIsNone(current_effect_1)
            self.assertEqual(current_effect_2.name, GameEffect.IN_TRADE)

        response = self._post_game_action(self.client_2, GameActionType.REJECT, disable_asserts=disable_assertions)
        responses.append(response)

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        if not disable_assertions:
            self.assertEqual(self.game.current_player, self.players[0])
            self.assertEqual(current_effect_1.name, GameEffect.ROLL_DICE)
            self.assertIsNone(current_effect_2)

        return responses

    def test_start_trade_success(self):
        self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=200,
            cash_received=100,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        self.assertEqual(self.game.current_player, self.players[1])
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_TRADE)
    
    def test_start_trade_error_dont_have_property(self):
        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=200,
            cash_received=100,
            ownerships=[
                2 # Property with id 2 doesn't exist
            ]
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Could not find ownership')

    def test_giving_more_money_than_player_has(self):
        player_1_money = self.players[0].cash

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=player_1_money + 10,
            cash_received=100,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'You are giving more money than you have')

    def test_asking_more_money_than_player_has(self):
        player_1_money = self.players[0].cash
        player_2_money = self.players[1].cash

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=player_1_money,
            cash_received=player_2_money + 1,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Other player doesn't have enough money to send")
    
    def test_reject_trade(self):
        self._start_trade_and_other_player_rejects()
    
    def test_that_just_giving_or_receiving_money_doesnt_work(self):
        cash_given = 200
        cash_received = 0

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=cash_given,
            cash_received=cash_received,
            ownerships=[]
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Invalid trade data")

        cash_given = 0
        cash_received = 100

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=cash_given,
            cash_received=cash_received,
            ownerships=[]
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Invalid trade data")

    def test_gifting_property(self):
        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=0,
            cash_received=0,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Invalid trade data")

    def test_accept_trade_with_everything(self):
        cash_given = 200
        cash_received = 100

        self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=cash_given,
            cash_received=cash_received,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()
        player_1_cash_before_trade = self.players[0].cash
        player_2_cash_before_trade = self.players[1].cash

        self.assertEqual(self.game.current_player, self.players[1])
        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.IN_TRADE)
        self.assertEqual(self.players[0].owned_properties.count(), 1)

        self._post_game_action(self.client_2, GameActionType.ACCEPT)

        self._refresh_game_and_players()
        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        self.assertEqual(self.game.current_player, self.players[0])
        self.assertEqual(current_effect_1.name, GameEffect.ROLL_DICE)
        self.assertEqual(current_effect_1.effect_data['trade_count'], 1)
        self.assertEqual(current_effect_1.effect_data['trade_accepted'], True)
        self.assertIsNone(current_effect_2)
        self.assertEqual(self.players[0].owned_properties.count(), 0)
        self.assertEqual(self.players[1].owned_properties.count(), 1)
        self.assertEqual(self.players[1].owned_properties.first().property.pk, self.player_1_ownership.property.pk)
        self.assertEqual(self.players[0].cash, player_1_cash_before_trade + (cash_received - cash_given))
        self.assertEqual(self.players[1].cash, player_2_cash_before_trade + (cash_given - cash_received))

    def test_creating_more_than_max_trades(self):
        for i in range(config.MAX_TRADE_PROPOSALS + 1):
            responses = self._start_trade_and_other_player_rejects(disable_assertions=True)

            if i < config.MAX_TRADE_PROPOSALS:
                for response in responses:
                    self.assertEqual(response.status_code, 200)
                    current_effect = self.players[0].get_current_effect()
                    self.assertEqual(current_effect.effect_data['trade_count'], i + 1)
                    self.assertEqual(current_effect.effect_data['trade_accepted'], False)
            else:
                create_trade_response = responses[0]
                reject_trade_response = responses[1]

                self.assertEqual(create_trade_response.status_code, 400)
                self.assertEqual(create_trade_response.json()['error'], f"You can't create more than {config.MAX_TRADE_PROPOSALS} trades in one turn")
                self.assertEqual(reject_trade_response.status_code, 400)
                self.assertEqual(reject_trade_response.json()['error'], "Unknown action or it's not your turn")

    def test_if_trade_accepted_then_no_more_trades_in_this_turn(self):
        self.test_accept_trade_with_everything()

        response = self._start_trade(
            from_player=self.players[0],
            to_player=self.players[1],
            cash_given=100,
            cash_received=100,
            ownerships=[
                self.player_1_ownership.pk
            ]
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "You can't create more trades in this turn")
    
    def test_trade_counter_is_reset_next_turn(self):
        self.test_creating_more_than_max_trades()
        resp = self._post_game_action(self.client_1, GameActionType.ROLL_DICE)
        self.assertEqual(resp.status_code, 200)
        self._refresh_game_and_players()

        # Now player is in ask_buy state, testing that he can't send trade while in ask_buy
        responses = self._start_trade_and_other_player_rejects(disable_assertions=True)
        for response in responses:
            self.assertEqual(response.status_code, 400)
        
        # Resolving ask_buy effect
        resp = self._post_game_action(self.client_1, GameActionType.START_AUCTION)
        resp = self._post_game_action(self.client_2, GameActionType.REJECT)
        resp = self._post_game_action(self.client_2, GameActionType.ROLL_DICE)
        self._refresh_game_and_players()

        current_effect_1 = self.players[0].get_current_effect()
        current_effect_2 = self.players[1].get_current_effect()

        self.assertIsNone(current_effect_1)
        self.assertEqual(current_effect_2.name, GameEffect.ASK_BUY)
        self.assertEqual(current_effect_2.effect_data['trade_count'], 0)
        
        self._post_game_action(self.client_2, GameActionType.START_AUCTION)
        self._post_game_action(self.client_1, GameActionType.REJECT)

        self.test_creating_more_than_max_trades()


class GameplayAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2)

        self.player_1, self.player_2 = self.players

        self._start_game()
        self._refresh_game_and_players()

    async def test_first_turn(self):
        communicator = self._get_ws_communicator(self.player_1)
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        message = await communicator.receive_json_from()
        self.assertEqual(WSEventType(message['type']), WSEventType.GAME_CONNECTED)

        self.assertEqual(self.game.turn, 1)
        self.assertEqual(self.game.current_player_id, self.player_1.pk)
        current_effect = await services.get_current_effect(self.player_1)
        self.assertEqual(current_effect.name, GameEffect.ROLL_DICE)

        resp = await self._post_game_action_async(self.client_1, GameActionType.ROLL_DICE)
        self.assertEqual(resp.status_code, 200)

        await self._refresh_game_and_players_async()

        message = await communicator.receive_json_from()
        players_data = message['players']

        self.assertEqual(WSEventType(message['type']), WSEventType.GAME_ACTION)
        players = [PlayerSerializer(data=player).initial_data for player in players_data]
        current_player = await services.get_player_by_id(self.game.current_player_id)
        test_dice_sum = sum(config.TEST_DICE_VALUES)

        for i, player in enumerate(players):
            self.assertEqual(player['id'], self.players[i].pk)
            self.assertEqual(player['cash'], config.STARTING_CASH)
            self.assertEqual(player['color'], self.players[i].color)
            self.assertEqual(player['in_jail'], False)
            self.assertEqual(player['jail_turns'], 0)
            if player['id'] == current_player.pk:
                self.assertEqual(player['position'], test_dice_sum)
                self.assertEqual(len(player['effects']), 1)
                current_effect = await services.get_current_effect(self.players[i])
                effect_from_gameframe = player['effects'][0]

                self.assertEqual(current_effect.name, GameEffect.ASK_BUY)
                self.assertEqual(effect_from_gameframe['name'], GameEffect.ASK_BUY)
                self.assertEqual(effect_from_gameframe['effect_data']['trade_count'], 0)
                self.assertEqual(effect_from_gameframe['effect_data']['trade_accepted'], False)
            else:
                self.assertEqual(player['position'], 0)
                self.assertEqual(player['effects'], [])
            self.assertEqual(player['status'], Player.PLAYING)
            self.assertEqual(player['move_backwards'], False)

        events = message['events']
        self.assertEqual(len(events), 2)
        self.assertEqual(WSEventType(events[0]['type']), WSEventType.GAME_ACTION)
        self.assertEqual(events[0]['action'], GameEventType.ROLL_DICE)
        self.assertEqual(events[0]['dices'], config.TEST_DICE_VALUES)

        self.assertEqual(WSEventType(events[1]['type']), WSEventType.GAME_ACTION)
        self.assertEqual(events[1]['action'], GameEventType.MOVE_PLAYER)
        self.assertEqual(events[1]['player'], self.player_1.pk)
        self.assertEqual(events[1]['position'], test_dice_sum)
