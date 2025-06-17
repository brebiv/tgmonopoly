from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import telebot
from telebot.types import (
    Message,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telebot import apihelper


if settings.USE_TELEGRAM_TEST_ENV:
    apihelper.API_URL = "https://api.telegram.org/bot{0}/test/{1}"


token = getattr(settings, "TG_BOT_TOKEN", None)
if token is None:
    raise ImproperlyConfigured("TG_BOT_TOKEN is not set")

bot = telebot.TeleBot(settings.TG_BOT_TOKEN, threaded=False)


@bot.message_handler(commands=["start"])
def welcome_handler(message: Message):
    # if settings.USE_TELEGRAM_TEST_ENV:
    #     if settings.USE_TELEGRAM_TEST_ENV_HTTPS:
    #         webapp_info = WebAppInfo("https://127.0.0.1:8000/")
    #     else:
    #         webapp_info = WebAppInfo("http://127.0.0.1:8000/")
    # else:
    #     webapp_info = WebAppInfo("https://dev-webapp.beatkeeper.me/")

    # keyboard = InlineKeyboardMarkup()
    # keyboard.add(InlineKeyboardButton("Start", web_app=webapp_info))

    # bot.send_message(message.chat.id, "Hi", reply_markup=keyboard)
    bot.send_message(message.chat.id, "Hello bitch")
