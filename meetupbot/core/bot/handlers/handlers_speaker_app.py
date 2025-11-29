from decimal import Decimal
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import Update

from core.models import SpeakerApplication, TelegramUser, Event
from core.services.speaker_app import create_speaker_app
from core.bot.keyboards.main_menu import get_main_menu_keyboard, get_speaker_keyboard

FULL_NAME = 1
AGE = 2
TOPIC_TITLE = 3
TOPIC_DESCRIPTION = 4

def handle_back(update: Update, user_id: int):
    is_spk = is_speaker(user_id)
    send_message_with_retry(
        update.message,
        "Вы в главном меню.",
        reply_markup=get_main_menu_keyboard(is_speaker=is_spk),
    )
    return ConversationHandler.END

def speaker_app_handler(update: Update, context: CallbackContext):
    context.user_data["speaker_app"] = {}
    update.message.reply_text("Ты начал заявку на спикера!")

    send_message_with_retry(
        update.message,
        "Ты хочешь стать спикером!\n\nВведи своё ФИО:",
        reply_markup=get_speaker_keyboard(),
    )
    
    return FULL_NAME

def speaker_app_full_name(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if text == "⬅️ Назад":
        return handle_back(update, user_id)

    context.user_data["speaker_app"]["full_name"] = text
    
    send_message_with_retry(
        update.message,
        "Введи свой возраст",
        reply_markup=get_speaker_keyboard(),
    )
    return AGE

def speaker_app_age(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if text == "⬅️ Назад":
        return handle_back(update, user_id)

    try:
        age = int(text)
        context.user_data["speaker_app"]["age"] = age
    except ValueError:
        send_message_with_retry(
            update.message,
            "Пожалуйста, введите корректный возраст числом.",
            reply_markup=get_speaker_keyboard(),
        )
        return AGE
    
    send_message_with_retry(
        update.message,
        "Расскажи тему своего доклада",
        reply_markup=get_speaker_keyboard(),
    )
    return TOPIC_TITLE


def speaker_app_topic_title(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if text == "⬅️ Назад":
        return handle_back(update, user_id)

    try:
        age = int(text)
        context.user_data["speaker_app"]["topic_title"] = text
    except ValueError:
        send_message_with_retry(
            update.message,
            "Пожалуйста, введите тему еще раз",
            reply_markup=get_speaker_keyboard(),
        )
        return TOPIC_TITLE
    
    send_message_with_retry(
        update.message,
        "Расскажи о чем хочешь рассказать",
        reply_markup=get_speaker_keyboard(),
    )
    return TOPIC_DESCRIPTION


def speaker_app_topic_description(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if text == "⬅️ Назад":
        return handle_back(update, user_id)

    context.user_data["speaker_app"]["topic_description"] = text
    speaker_data = context.user_data["speaker_app"]
    
    try:
        telegram_user = TelegramUser.objects.get(id=user_id)
        event = None 
        create_speaker_app(
            user=telegram_user,
            event=event,
            data=speaker_data
        )

        confirmation_message = (
            f"Спасибо! Ваша заявка отправлена.\n"
            f"ФИО: {speaker_data['full_name']}\n"
            f"Возраст: {speaker_data['age']}\n"
            f"Тема доклада: {speaker_data['topic_title']}\n"
            f"Описание темы: {speaker_data['topic_description']}"
        )

        send_message_with_retry(
            update.message,
            confirmation_message,
            reply_markup=get_speaker_keyboard(),
        )
    except ValueError as e:
        send_message_with_retry(
            update.message,
            str(e),
            reply_markup=get_speaker_keyboard(),
        )

    return ConversationHandler.END
