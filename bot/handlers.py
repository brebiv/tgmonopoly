import telebot
from telebot.types import (
    Message,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from .utils import _configure_telegram_env, get_token, _get_webapp_origin

_configure_telegram_env()
bot = telebot.TeleBot(get_token(), threaded=False)


@bot.message_handler(commands=["start"])
def welcome_handler(message: Message):
    webapp_info = WebAppInfo(_get_webapp_origin())

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Start", web_app=webapp_info))

    bot.send_message(message.chat.id, "Science, Bitch!", reply_markup=keyboard)
