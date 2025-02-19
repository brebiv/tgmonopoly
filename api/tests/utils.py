from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TestCase, Client
from django.http import HttpResponse
from django.urls import reverse
from unittest.mock import patch

from tgmonopoly.asgi import application as tgmonopoly_application
from bot.models import TelegramUser
from game.models import Game, Player, GameEffect, Property
from game import config
from api.tests import data as test_data
from api.types import GameActionType
from api.serializers import GameActionSerializer


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
    
    def _create_game(self, num_players: 2 | 3, auto_join: bool = True):
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

        if auto_join:
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
        """After adding auto-start on game join this function is no longer needed"""
        if config.ENABLE_AUTO_START_ON_JOIN:
            return
        else:
            response = self.client_1.post(
                reverse('game_action'),
                data={
                    'action': GameActionType.START_GAME,
                    'game_uuid': self.game.uuid,
                }
            )
            self.assertEqual(response.status_code, 200)

    @patch('game.services.GameService._roll_dice_values')
    def _start_game_and_begin_auction_flow(self, mock_roll_dice_values):
        """
        Helper method that encapsulates the logic of:
         1) Starting the game
         2) Attempting to start an auction from start tile (which should fail)
         3) Rolling dice
         4) Attempting to start an auction from the correct tile
        """
        dices_values = config.TEST_DICE_VALUES
        mock_roll_dice_values.return_value = dices_values
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