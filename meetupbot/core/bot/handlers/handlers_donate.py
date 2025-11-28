from decimal import Decimal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

from core.models import TelegramUser, Event
from core.services.donations import create_pending_donation, mark_donation_paid

ASK_AMOUNT = 1


def donate_entry(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Поддержать митап", callback_data="donate_yes"),
            InlineKeyboardButton("Не сейчас", callback_data="donate_no"),
        ]
    ]
    update.message.reply_text(
        "Хочешь поддержать организаторов митапа? ",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return ASK_AMOUNT


def donate_choice(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "donate_no":
        query.edit_message_text("Окей, главное, что ты с нами ")
        return ConversationHandler.END

    # donate_yes
    query.edit_message_text("Напиши сумму доната в рублях, например: 200")
    return ASK_AMOUNT


def donate_set_amount(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    try:
        amount = Decimal(text.replace(",", "."))
    except Exception:
        update.message.reply_text("Не смог понять сумму  Напиши число, например: 200")
        return ASK_AMOUNT

    tg_user = update.effective_user
    db_user, _ = TelegramUser.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={"username": tg_user.username or ""}
    )

    # TODO: получить текущий Event
    event = Event.objects.filter(is_current=True).first()

    donation = create_pending_donation(
        user=db_user,
        event=event,
        amount=amount,
        provider="fake",
    )

    # сейчас просто сразу помечаем как оплаченный
    mark_donation_paid(donation)

    update.message.reply_text(
        f"Спасибо за поддержку на {amount} ₽! \n"
        f"(пока это тестовый донат, без реальной оплаты)"
    )
    return ConversationHandler.END
