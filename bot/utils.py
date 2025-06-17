from telebot.types import Message, CallbackQuery, InlineQuery

from . import models


def user_handler(function):
    def wrapper(message):
        if isinstance(message, Message, CallbackQuery, InlineQuery):
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
