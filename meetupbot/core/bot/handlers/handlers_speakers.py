from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from django.utils import timezone

from core.models import Event, TelegramUser, SpeakerProfile
from core.bot.keyboards.main_menu import (
    get_speakers_keyboard,
    get_speaker_keyboard,
)

CHOOSING_SPEAKER = 1


def _get_current_event():
    """Внутренняя функция: найти текущее или ближайшее мероприятие."""
    now = timezone.now().date()

    event = Event.objects.filter(is_current=True).order_by("date").first()
    if event:
        return event

    event = (
        Event.objects.filter(is_active=True, date__gte=now)
        .order_by("date")
        .first()
    )
    return event


def show_speakers_entry(update: Update, context: CallbackContext):
    """
    Обработчик кнопки 'ФИО выступающих'.

    Показывает список имён спикеров текущего/ближайшего мероприятия.
    """
    event = _get_current_event()
    if not event:
        update.message.reply_text(
            "Сейчас нет активных мероприятий, поэтому список спикеров пуст"
        )
        return ConversationHandler.END

    # Находим всех спикеров, у которых есть доклад на этом мероприятии
    speakers_qs = (
        TelegramUser.objects.filter(talks__event=event)
        .distinct()
    )

    if not speakers_qs.exists():
        update.message.reply_text(
            "Для этого мероприятия спикеры ещё не указаны "
        )
        return ConversationHandler.END

    # Готовим список для клавиатуры и карту имя -> id в user_data
    speakers = []
    speakers_map = {}

    for user in speakers_qs:
        name = user.first_name or user.username or f"Спикер {user.id}"
        speakers.append({"id": user.id, "name": name})
        speakers_map[name] = user.id

    context.user_data["speakers_map"] = speakers_map

    update.message.reply_text(
        "Выбери выступающего, чтобы посмотреть его биографию:",
        reply_markup=get_speakers_keyboard(speakers),
    )
    return CHOOSING_SPEAKER


def show_speaker_bio(update: Update, context: CallbackContext):
    """
    Пользователь нажал кнопку с ФИО спикера.
    Показываем его биографию (или заглушку, если её нет).
    """
    text = update.message.text.strip()

    # Назад — просто выходим из диалога
    if text in ("Назад", "⬅️ Назад", " Назад"):
        update.message.reply_text("Окей, вернёмся в меню")
        return ConversationHandler.END

    speakers_map = context.user_data.get("speakers_map") or {}
    speaker_id = speakers_map.get(text)

    if not speaker_id:
        update.message.reply_text(
            "Не смог найти такого спикера 🤔 Попробуй выбрать из списка ещё раз."
        )
        return CHOOSING_SPEAKER

    speaker = TelegramUser.objects.filter(id=speaker_id).first()
    if not speaker:
        update.message.reply_text("Что-то пошло не так, спикер не найден ")
        return ConversationHandler.END

    profile = SpeakerProfile.objects.filter(user=speaker).first()

    if profile and profile.bio:
        bio_text = profile.bio
    else:
        bio_text = "Биография этого спикера пока не заполнена "

    update.message.reply_text(
        bio_text,
        reply_markup=get_speaker_keyboard(),  # маленькая клавиатура, можно потом сделать 'В меню'
    )
    return ConversationHandler.END
