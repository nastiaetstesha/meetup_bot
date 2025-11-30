# для управления ботом через команду Django - python manage.py run_bot

from django.core.management.base import BaseCommand

from apscheduler.schedulers.background import BackgroundScheduler
from core.services.networking_cleanup import clear_networking_profiles

from core.bot.bot import build_updater


class Command(BaseCommand):
    help = "Запуск Telegram-бота Meetup"

    def handle(self, *args, **options):
        updater = build_updater()

        scheduler = BackgroundScheduler(timezone="Europe/Moscow")
        scheduler.add_job(clear_networking_profiles, "cron", hour=0, minute=0)
        scheduler.start()
        
        self.stdout.write(self.style.SUCCESS("Bot started..."))
        
        updater.start_polling()
        updater.idle()
