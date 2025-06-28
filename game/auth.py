from urllib.parse import parse_qs
from typing import Optional
import hashlib
import hmac
import json

from rest_framework.request import Request
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission

from bot import utils as bot_utils
from bot.models import TelegramUser
from game.utils import update_or_create_telegram_user


class CustomRequest(Request):
    is_telegram_authenticated: bool = False
    telegram_user: Optional[TelegramUser] = None


class IsTelegramAuthenticated(BasePermission):
    """
    Allows access only when the TelegramWebAppAuthentication
    decorator has verified the request.
    """

    message = "Telegram Web App authentication required"

    def has_permission(self, request, _):
        return getattr(request, "is_telegram_authenticated", False) and getattr(
            request, "telegram_user", False
        )


class TelegramWebAppAuthentication(BaseAuthentication):
    header_prefix = "TWA"

    def verify_telegram_init_data(self, init_data: dict, bot_token: str) -> bool:
        """
        Value in the Authorization header is expected to be coming from `window.Telegram.WebApp.initData` in the frontend

        docs: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
        """

        try:
            hash = init_data.pop("hash")
        except KeyError:
            return False

        data_check = sorted([f"{key}={value}" for key, value in init_data.items()])
        data_check_string = "\n".join(data_check)
        secret_key = hmac.new(
            "WebAppData".encode(), bot_token.encode(), hashlib.sha256
        ).digest()
        verification_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(verification_hash, hash)

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        auth_header_value = auth_header.split(": ", 1)[-1]

        try:
            auth_type, auth_data = auth_header_value.split(" ", 1)
        except ValueError:
            return None

        if auth_type != self.header_prefix:
            return None

        auth_data_dict = {k: v[0] for k, v in parse_qs(auth_data).items()}
        if not self.verify_telegram_init_data(auth_data_dict, bot_utils.get_token()):
            raise AuthenticationFailed("Invalid Telegram auth data")

        user_data = json.loads(auth_data_dict["user"])
        user = update_or_create_telegram_user(user_data)
        if user.ban:
            raise PermissionDenied("User is banned")

        request.telegram_user = user
        request.is_telegram_authenticated = True

        # Returning (None, None), so that Django wont override the default Django request.user
        return (None, None)
