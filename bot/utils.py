from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from telebot.types import Message, CallbackQuery, InlineQuery
from telebot import apihelper

from . import models


def user_handler(function):
    def wrapper(message):
        if isinstance(message, (Message, CallbackQuery, InlineQuery)):
            try:
                user = models.TelegramUser.objects.get(user_id=message.from_user.id)
                if user.ban:
                    return

                # Snippet for banning based on tg_id, username, etc.
                # if user.user_id = ''
            except models.TelegramUser.DoesNotExist:
                user = models.TelegramUser(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    language=message.from_user.language_code or "?",
                )
            else:
                user.username = message.from_user.username
                user.first_name = message.from_user.first_name
                user.last_name = message.from_user.last_name
                user.language = message.from_user.language_code
            finally:
                user.save()
            return function(message, user)

    return wrapper


def get_token() -> str:
    token = getattr(settings, "TG_BOT_TOKEN", None)
    if token is None:
        raise ImproperlyConfigured("TG_BOT_TOKEN is not set")
    return token


def _configure_telegram_env():
    if settings.TG_USE_TEST_ENV:
        if settings.TG_USE_TEST_ENV_HTTPS:
            apihelper.API_URL = "https://api.telegram.org/bot{0}/test/{1}"
        else:
            apihelper.API_URL = "http://api.telegram.org/bot{0}/test/{1}"


def _get_webapp_origin() -> str:
    origin = getattr(settings, "TG_WEBAPP_ORIGIN", None)
    if origin is None:
        raise ImproperlyConfigured("TG_WEBAPP_ORIGIN is not set")

    return origin
