from django.conf import settings
from telebot.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import telebot

from telebot import apihelper


if settings.USE_TELEGRAM_TEST_ENV:
    apihelper.API_URL = 'https://api.telegram.org/bot{0}/test/{1}'

bot = telebot.TeleBot(settings.BOT_TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    
    webapp_info = WebAppInfo('http://127.0.0.1:8000/')

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Start", web_app=webapp_info))

    bot.send_message(message.chat.id, "Hi", reply_markup=keyboard)
