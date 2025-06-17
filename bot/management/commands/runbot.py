from django.core.management.base import BaseCommand
from bot.handlers import bot


class Command(BaseCommand):
    help = "Started Telegram bot in long-polling mode"

    def handle(self, *args, **options):
        self.stdout.write("Starting bot in long-polling mode. To stop it, press Ctrl+C")
        bot.infinity_polling()
