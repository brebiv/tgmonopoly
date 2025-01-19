from urllib.parse import parse_qs
from functools import wraps
from typing import Optional
import hashlib
import hmac
import json
import sys

from django.conf import settings
from django.http import HttpResponseForbidden, HttpRequest
from rest_framework.request import Request as DRFRequest

from bot.models import TelegramUser


class CustomRequest(HttpRequest, DRFRequest):
    is_telegram_authenticated: bool
    telegram_user: Optional[TelegramUser]


def validate_telegram_webapp_data(data: dict) -> bool:
    required_keys = {"query_id", "user", "auth_date", "hash"}
    
    if not required_keys.issubset(data.keys()):
        return False
    
    try:
        user_data = json.loads(data['user'])
        required_user_keys = {"id", "first_name", "last_name", "language_code", "allows_write_to_pm"}
        if not required_user_keys.issubset(user_data.keys()):
            return False
        if not isinstance(user_data["id"], int):
            return False
        if not isinstance(user_data["allows_write_to_pm"], bool):
            return False
    except (json.JSONDecodeError, TypeError):
        return False

    try:
        auth_date = int(data['auth_date'])
    except ValueError:
        return False
    
    return True


def verify_telegram_init_data(init_data: dict, bot_token: str) -> bool:
    """Don't touch. Thank god it works.
    `init_data` is a result of running `{k: v[0] for k, v in parse_qs(auth_data).items()}`
    auth_data is string that is passed from `window.Telegram.WebApp.initData` in the frontend
    """

    if not validate_telegram_webapp_data(init_data):
        return False
    
    hash = init_data.pop('hash')
    data_check = sorted([f"{key}={value}" for key, value in init_data.items()])
    data_check_string = '\n'.join(data_check)
    secret_key = hmac.new('WebAppData'.encode(), bot_token.encode(), hashlib.sha256).digest()
    verification_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return verification_hash == hash


def parse_user_from_qs(init_data_raw: str) -> TelegramUser:
    init_data = {k: v[0] for k, v in parse_qs(init_data_raw).items()}
    user_data = json.loads(init_data.get('user'))
    if user_data == None:
        return None
    
    user = TelegramUser.objects.get(user_id=int(user_data['id']))
    return user


def telegram_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request: CustomRequest, *args, **kwargs):
        auth_header = request.headers.get('AUTHORIZATION')

        # if settings.DEBUG:
        #     client_ip = request.META.get('REMOTE_ADDR')
        #     if client_ip in settings.WHITELISTED_IPS:
        #         user = TelegramUser.objects.first()
        #         request.is_telegram_authenticated = user != None
        #         request.telegram_user = user
        #         return view_func(request, *args, **kwargs)

        if auth_header:
            parts = auth_header.split(' ', 1)
            
            if len(parts) == 2:
                auth_type, auth_data = parts

                if auth_type == 'twa':
                    auth_data = {k: v[0] for k, v in parse_qs(auth_data).items()}

                    is_hash_correct = verify_telegram_init_data(auth_data, settings.BOT_TOKEN)

                    if not is_hash_correct:
                        return HttpResponseForbidden("Forbidden")

                    user_data = json.loads(auth_data.get('user'))
                    if user_data == None:
                        return HttpResponseForbidden("Forbidden")

                    try:
                        user = TelegramUser.objects.get(user_id=int(user_data['id']))
                        if user.ban:
                            return
                        # if user.user_id = ''
                    except TelegramUser.DoesNotExist:
                        user = TelegramUser(
                            user_id=user_data.get('id'),
                            username=user_data.get('username', ''),
                            first_name=user_data.get('first_name', ''),
                            last_name=user_data.get('last_name', ''),
                            language=user_data.get('language_code', '')
                        )
                    else:
                        pass
                        # user.username = message.from_user.username
                        # user.first_name = message.from_user.first_name
                        # user.last_name = message.from_user.last_name
                        # user.language = message.from_user.language_code
                    finally:
                        user.save()
            
                    request.is_telegram_authenticated = is_hash_correct and user != None
                    request.telegram_user = user
                else:
                    request.is_telegram_authenticated = False
            else:
                request.is_telegram_authenticated = False
        else:
            request.is_telegram_authenticated = False

        if request.is_telegram_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Forbidden")

    return _wrapped_view


def is_running_tests():
    return 'test' in sys.argv or settings.TESTING
