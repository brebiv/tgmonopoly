from django.test import TestCase, Client
from django.urls import reverse
from game.models import Game
from celery.contrib.testing.worker import start_worker

from . import data as test_data
from api.types import GameActionType
from api.utils import parse_user_from_qs
from bot.models import TelegramUser


# Create your tests here.
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


class CreateGameTest(TestCase):
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
