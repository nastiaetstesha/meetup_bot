from decimal import Decimal
from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update
from telegram import ReplyKeyboardMarkup

from core.models import FutureEventSubscription, TelegramUser
from core.services.subscriptions import create_subscriptions
from core.bot.keyboards.main_menu import get_main_menu_keyboard, get_speaker_keyboard, BACK_BUTTON



exit_keyboard = ReplyKeyboardMarkup(
    [["Вернуться в меню"]],
    resize_keyboard=True
)


NAME = 1
COMMENT = 2


def subscriptions_handler(update, context):
    context.user_data["subscriptions"] = {}
    update.message.reply_text("Ты решил оформить подписку на следующие мероприятия.\n\n Введи свое имя:")

    return NAME

def subscriptions_name(update, context):

    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    context.user_data["subscriptions"]["name"] = update.message.text
    update.message.reply_text("Здесь ты можешь оставить комментраий или пожелания для следующих мероприятий", reply_markup=exit_keyboard)

    return COMMENT

def subscriptions_comment(update, context):
    if update.message.text == "Вернуться в меню":
        update.message.reply_text(
            "Вы вернулись в главное меню",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END
    
    subscriptions_data = context.user_data.get("subscriptions", {})
    subscriptions_data["comment"] = update.message.text

    tg_user = update.effective_user
    telegram_user, _ = TelegramUser.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={"username": tg_user.username or ""},
    )

    try:
        app = create_subscriptions(
            user=telegram_user,
            data=subscriptions_data
        )

        confirmation_message = (
            "Спасибо! Вы подписались на следующие мероприятия!.\n\n"
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

