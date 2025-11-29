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

from core.bot.handlers.handlers_donate import (
    donate_entry,
    donate_choice,
    donate_set_amount,
    ASK_AMOUNT,
)
from core.bot.handlers.handlers_networking import (
    networking_start,
    profile_fill_name,
    profile_fill_age,
    profile_fill_stack,
    profile_fill_goal,
    profile_menu_handler,
    PROFILE_FILL_NAME,
    PROFILE_FILL_AGE,
    PROFILE_FILL_STACK,
    PROFILE_FILL_GOAL,
    PROFILE_SHOW_MENU,
    MATCH_MENU,
    match_menu_handler,
)
from core.bot.handlers.handlers_schedule import show_today_schedule
from core.bot.handlers.handlers_speakers import (
    show_speakers_entry,
    show_speaker_bio,
    CHOOSING_SPEAKER,
)
from core.bot.handlers.handlers_questions import (
    ask_question_entry,
    ask_question_choose_talk,
    ask_question_write,
    enter_speaker_mode,
    show_speaker_questions,
    speaker_still_talking,
    speaker_finished,
    CHOOSE_TALK,
    WRITE_QUESTION,
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


    #Диалог "Познакомиться"
    networking_conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(r"^Познакомиться$"), networking_start),
        ],
        states={
            PROFILE_FILL_NAME: [
                MessageHandler(Filters.text & ~Filters.command, profile_fill_name),
            ],
            PROFILE_FILL_AGE: [
                MessageHandler(Filters.text & ~Filters.command, profile_fill_age),
            ],
            PROFILE_FILL_STACK: [
                MessageHandler(Filters.text & ~Filters.command, profile_fill_stack),
            ],
            PROFILE_FILL_GOAL: [
                MessageHandler(Filters.text & ~Filters.command, profile_fill_goal),
            ],
            PROFILE_SHOW_MENU: [
                MessageHandler(Filters.text & ~Filters.command, profile_menu_handler),
            ],
            MATCH_MENU: [
                MessageHandler(Filters.text & ~Filters.command, match_menu_handler),
            ],
        },
        fallbacks=[],
    )

    dp.add_handler(networking_conv)

        # Афиша на сегодня
    dp.add_handler(
        MessageHandler(Filters.regex(r"^Афиша на сегодня$"), show_today_schedule)
    )

    # Список спикеров + биография
    speakers_conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(r"^ФИО выступающих$"), show_speakers_entry),
        ],
        states={
            CHOOSING_SPEAKER: [
                MessageHandler(Filters.text & ~Filters.command, show_speaker_bio),
            ],
        },
        fallbacks=[],
    )
    dp.add_handler(speakers_conv)

    # слушатель: задать вопрос
    ask_question_conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(r"^Задать вопрос$"), ask_question_entry),
        ],
        states={
            CHOOSE_TALK: [
                MessageHandler(Filters.text & ~Filters.command, ask_question_choose_talk),
            ],
            WRITE_QUESTION: [
                MessageHandler(Filters.text & ~Filters.command, ask_question_write),
            ],
        },
        fallbacks=[],
    )
    dp.add_handler(ask_question_conv)

    # спикер: вход в режим
    dp.add_handler(
        MessageHandler(Filters.regex(r"^Я спикер$"), enter_speaker_mode)
    )

    # спикер: посмотреть вопросы
    dp.add_handler(
        MessageHandler(Filters.regex(r"^Вопросы$"), show_speaker_questions)
    )

    # спикер: ещё выступаю
    dp.add_handler(
        MessageHandler(Filters.regex(r"^Еще выступаю$"), speaker_still_talking)
    )

    # спикер: завершил выступление
    dp.add_handler(
        MessageHandler(Filters.regex(r"^Выступил$"), speaker_finished)
    )

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
