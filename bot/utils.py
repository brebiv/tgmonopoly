from django.conf import settings
from typing import List

from telebot.types import CallbackQuery, Message, InlineQuery, InlineKeyboardButton, InlineKeyboardMarkup

# from bot import texts

from . import models
from game.models import Player, Game


def user_handler(function):
    def wrapper(message):
        if isinstance(message, Message):
            try:
                user = models.TelegramUser.objects.get(user_id=message.from_user.id)
                if user.ban:
                    return
                # if user.user_id = ''
            except models.TelegramUser.DoesNotExist:
                user = models.TelegramUser(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    language=message.from_user.language_code or '?'
                )
            else:
                user.username = message.from_user.username
                user.first_name = message.from_user.first_name
                user.last_name = message.from_user.last_name
                user.language = message.from_user.language_code
            finally:
                user.save()
            return function(message, user)
        elif isinstance(message, CallbackQuery):
            call: CallbackQuery = message
            try:
                user = models.TelegramUser.objects.get(user_id=call.from_user.id)
                if user.ban:
                    return
            except models.TelegramUser.DoesNotExist:
                user = models.TelegramUser(
                    user_id=call.from_user.id,
                    username=call.from_user.username,
                    first_name=call.from_user.first_name,
                    last_name=call.from_user.last_name,
                    language=call.from_user.language_code or '?'
                )
            else:
                user.username = call.from_user.username
                user.first_name = call.from_user.first_name
                user.last_name = call.from_user.last_name
                user.language = call.from_user.language_code
            finally:
                user.save()
            return function(call, user)
        elif isinstance(message, InlineQuery):
            inline_query: InlineQuery = message
            try:
                user = models.TelegramUser.objects.get(user_id=inline_query.from_user.id)
                if user.ban:
                    return
            except models.TelegramUser.DoesNotExist:
                user = models.TelegramUser(
                    user_id=inline_query.from_user.id,
                    username=inline_query.from_user.username,
                    first_name=inline_query.from_user.first_name,
                    last_name=inline_query.from_user.last_name,
                    language=inline_query.from_user.language_code or '?'
                )
            else:
                user.username = inline_query.from_user.username
                user.first_name = inline_query.from_user.first_name
                user.last_name = inline_query.from_user.last_name
                user.language = inline_query.from_user.language_code
            finally:
                user.save()
            return function(inline_query, user)
    return wrapper
