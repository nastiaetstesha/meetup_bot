from decimal import Decimal
from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update
from telegram import ReplyKeyboardMarkup

from core.models import SpeakerApplication, TelegramUser, Event
from core.services.speaker_app import create_speaker_app
from core.bot.keyboards.main_menu import get_main_menu_keyboard, get_speaker_keyboard, BACK_BUTTON
from django.utils import timezone # хз 


exit_keyboard = ReplyKeyboardMarkup(
    [["Вернуться в меню"]],
    resize_keyboard=True
)


FULL_NAME = 1
AGE = 2
TOPIC_TITLE = 3
TOPIC_DESCRIPTION = 4

def speaker_app_handler(update, context):
    context.user_data["speaker_app"] = {}
    update.message.reply_text("Ты хочешь стать спикером!\n\nВведи своё ФИО:")

    return FULL_NAME

def speaker_app_full_name(update, context):

    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    context.user_data["speaker_app"]["full_name"] = update.message.text
    update.message.reply_text("Введи свой возраст", reply_markup=exit_keyboard)

    return AGE

def speaker_app_age(update, context):
    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END
    
    context.user_data["speaker_app"]["age"] = update.message.text
    update.message.reply_text("Расскажи тему своего доклада", reply_markup=exit_keyboard)
    return TOPIC_TITLE


def speaker_app_topic_title(update, context):
    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END
    
    context.user_data["speaker_app"]["topic_title"] = update.message.text
    update.message.reply_text("Расскажи о чем хочешь рассказать", reply_markup=exit_keyboard)

    return TOPIC_DESCRIPTION


def speaker_app_topic_description(update: Update, context: CallbackContext):
    if update.message.text == "Вернуться в меню":
        update.message.reply_text(
            "Вы вернулись в главное меню",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END
    
    speaker_data = context.user_data.get("speaker_app", {})
    speaker_data["topic_description"] = update.message.text

    # 1. находим/создаём TelegramUser
    tg_user = update.effective_user
    telegram_user, _ = TelegramUser.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={"username": tg_user.username or ""},
    )

    # 2. текущий ивент (если есть)
    event = Event.objects.filter(is_current=True).first()

    try:
        app = create_speaker_app(
            user=telegram_user,
            event=event,
            data=speaker_data,
        )

        confirmation_message = (
            "Спасибо! Ваша заявка отправлена.\n\n"
            f"ФИО: {speaker_data['full_name']}\n"
            f"Возраст: {speaker_data['age']}\n"
            f"Тема доклада: {speaker_data['topic_title']}\n"
            f"Описание темы: {speaker_data['topic_description']}"
        )

        update.message.reply_text(
            confirmation_message,
            reply_markup=get_main_menu_keyboard(is_speaker=False),
        )

    except Exception as e:
        update.message.reply_text(
            f"Произошла ошибка при сохранении заявки: {e}",
            reply_markup=get_main_menu_keyboard(is_speaker=False),
        )

    return ConversationHandler.END
