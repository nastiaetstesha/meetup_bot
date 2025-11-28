import os
import logging

from django.conf import settings

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    Filters,
)

from meetupbot.core.bot.handlers.handlers_donate import (
    donate_entry,
    donate_choice,
    donate_set_amount,
    ASK_AMOUNT,
)
from core.bot.keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)


def start(update, context):
    """Простой /start и показ главного меню."""
    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.first_name or 'друг'}! Это бот Python Meetup 🤖",
        reply_markup=get_main_menu_keyboard(is_speaker=False),
    )


def build_updater() -> Updater:
    # токен берём из настроек Django
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан ни в settings, ни в переменных окружения")

    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    # /start
    dp.add_handler(CommandHandler("start", start))

    # диалог доната:
    # - вход по кнопке "Донат" из обычной клавиатуры
    donate_conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(r"^Донат$"), donate_entry),
        ],
        states={
            ASK_AMOUNT: [
                CallbackQueryHandler(donate_choice, pattern=r"^donate_(yes|no)$"),
                MessageHandler(Filters.text & ~Filters.command, donate_set_amount),
            ],
        },
        fallbacks=[],
    )

    dp.add_handler(donate_conv)

    logger.info("Handlers registered")
    return updater
