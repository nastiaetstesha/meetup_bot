# для управления ботом через команду Django - python manage.py run_bot

from django.core.management.base import BaseCommand

from core.bot.bot import build_updater


class Command(BaseCommand):
    help = "Запуск Telegram-бота Meetup"

    def handle(self, *args, **options):
        updater = build_updater()
        self.stdout.write(self.style.SUCCESS("Bot started..."))
        updater.start_polling()
        updater.idle()
