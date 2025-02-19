import unittest
from django.urls import reverse
from django.test import TestCase, Client

from api.tests import data as test_data
from bot.models import TelegramUser
from game.models import Game
from game import config
from .utils import BaseAPITestCase


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


class GameListAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        if config.ENABLE_AUTO_START_ON_JOIN:
            self._create_game(2, False)
        else:
            self._create_game(2, True)

    def test_game_list(self):
        response = self.client_1.get(reverse('game_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertEqual(len(response.json()['games']), 1)

        game = Game.objects.get(uuid=response.json()['games'][0]['uuid'])
        self.assertEqual(game.max_players, 2)
        self.assertEqual(game.status, Game.WAITING)

    @unittest.mock.patch('game.config.ALLOW_CREATING_MULTIPLE_GAMES', True)
    def test_game_list_filtered_by_status(self):
        response = self.client_1.get(reverse('game_list'), {'status': 1})   # Playing
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertEqual(len(response.json()['games']), 0)

        response = self.client_1.get(reverse('game_list'), {'status': 2})   # Finished
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertEqual(len(response.json()['games']), 0)

        response = self.client_1.get(reverse('game_list'), {'status': 0})   # Waiting
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertEqual(len(response.json()['games']), 1)

        if config.ENABLE_AUTO_START_ON_JOIN:
            self._create_game(2)

            response = self.client_1.get(reverse('game_list'), {'status': 1})   # Playing
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['status'], 'ok')
            self.assertEqual(len(response.json()['games']), 1)

            response = self.client_1.get(reverse('game_list'), {'status': 0})   # Waiting
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['status'], 'ok')
            self.assertEqual(len(response.json()['games']), 1)

    @unittest.mock.patch('game.config.ALLOW_CREATING_MULTIPLE_GAMES', True)
    def test_game_list_pagination(self):
        for i in range(20):
            self._create_game(2, False)
        
        response = self.client_1.get(reverse('game_list'), {'status': 0})
        resp_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['status'], 'ok')
        self.assertEqual(len(resp_data['games']), 10)
        self.assertIn('next_url', resp_data)
        self.assertIn('status=', resp_data['next_url'])
        self.assertIn('page=2', resp_data['next_url'])


class JoinGameAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(2, auto_join=False)

    @unittest.skipIf(not config.ENABLE_AUTO_START_ON_JOIN, "if auto-start is not enabled skip it")
    def test_join_game_and_auto_start(self):
        self.assertEqual(self.game.players.count(), 1)

        resp = self.client_2.post(
            reverse('join_game'),
            data={
                'game_uuid': self.game.uuid
            }
        )
        self.assertEqual(resp.status_code, 200)

        self.players = self.game.players.all()
        self.player_1, self.player_2 = self.players
        self._refresh_game_and_players()

        self.assertEqual(self.game.status, Game.PLAYING)
        self.assertEqual(self.game.players.count(), 2)
    
    def test_join_game_twice(self):
        self.assertEqual(self.game.players.count(), 1)

        resp = self.client_1.post(
            reverse('join_game'),
            data={
                'game_uuid': self.game.uuid
            }
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], "You are already playing this game")
        self.assertEqual(self.game.status, Game.WAITING)
        self.assertEqual(self.game.players.count(), 1)

    @unittest.skipIf(config.ENABLE_AUTO_START_ON_JOIN, "Deprecated, because of auto-start on game join")
    def test_join_game_full(self):
        self.assertEqual(self.game.players.count(), 1)

        resp = self.client_2.post(
            reverse('join_game'),
            data={
                'game_uuid': self.game.uuid
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.game.status, Game.WAITING)
        self.assertEqual(self.game.players.count(), 2)

        resp = self.client_3.post(
            reverse('join_game'),
            data={
                'game_uuid': self.game.uuid
            }
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], "Game is full")
        self.assertEqual(self.game.status, Game.WAITING)
        self.assertEqual(self.game.players.count(), 2)

    def test_join_playing_game(self):
        resp = self.client_2.post(
            reverse('join_game'),
            data={
                'game_uuid': self.game.uuid
            }
        )
        self.assertEqual(resp.status_code, 200)
        self._refresh_game_and_players()
        self.assertEqual(self.game.players.count(), 2)

        if config.ENABLE_AUTO_START_ON_JOIN:
            self.assertEqual(self.game.status, Game.PLAYING)
        else:
            self.assertEqual(self.game.status, Game.WAITING)
            self._start_game()


        resp = self.client_3.post(
            reverse('join_game'),
            data={
                'game_uuid': self.game.uuid
            }
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], "Game is not in waiting state")
        self._refresh_game_and_players()
        self.assertEqual(self.game.status, Game.PLAYING)
        self.assertEqual(self.game.players.count(), 2)


class LeaveGameAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.enable_logging = False
        self._create_game(3, auto_join=False)
    
    def test_leave_game_in_waiting(self):
        self.assertEqual(self.game.players.count(), 1)

        resp = self.client_2.post(
            reverse('join_game'),
            data={
                'game_uuid': self.game.uuid
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.game.status, Game.WAITING)
        self.assertEqual(self.game.players.count(), 2)

        resp = self.client_2.get(reverse('leave_game', kwargs={'game_uuid': self.game.uuid}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.game.status, Game.WAITING)
        self.assertEqual(self.game.players.count(), 1)

    @unittest.skip("Not implemented")
    def test_leave_game_in_playing(self):
        pass
