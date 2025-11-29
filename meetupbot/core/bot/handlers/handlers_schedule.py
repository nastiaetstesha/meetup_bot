from telegram import Update
from telegram.ext import CallbackContext
from django.utils import timezone

from core.models import Event, Talk
from core.bot.keyboards.main_menu import get_schedule_keyboard


def show_today_schedule(update: Update, context: CallbackContext):
    """
    Обработчик кнопки 'Афиша на сегодня'.

    1) Ищет текущее (is_current) или ближайшее активное мероприятие.
    2) Если его нет — пишет, что мероприятий пока нет.
    3) Если нет докладов — пишет, что программа формируется.
    4) Если есть доклады — показывает список и выдаёт клавиатуру
       с кнопкой 'ФИО выступающих'.
    """
    now = timezone.now().date()

    # 1. "Текущее" мероприятие
    event = Event.objects.filter(is_current=True).order_by("date").first()

    # 2. Если текущего нет — ближайшее активное
    if not event:
        event = (
            Event.objects.filter(is_active=True, date__gte=now)
            .order_by("date")
            .first()
        )

    # 3. Если вообще нет мероприятий
    if not event:
        update.message.reply_text(
            "Пока нет запланированных мероприятий 🥲\n"
            "Следи за обновлениями — скоро что-то обязательно появится!"
        )
        return

    # 4. Берём доклады
    talks = event.talks.all().order_by("start_at", "order")

    if not talks.exists():
        update.message.reply_text(
            f"Ближайшее мероприятие:\n"
            f"• {event.title}\n"
            f"• Дата: {event.date.strftime('%d.%m.%Y')}\n\n"
            f"Программа ещё формируется, афиша появится позже 🙂"
        )
        return

    # 5. Собираем текст афиши
    lines = [
        f"📅 Афиша на {event.date.strftime('%d.%m.%Y')}",
        f"Мероприятие: {event.title}",
        "",
    ]

    for idx, talk in enumerate(talks, start=1):
        if talk.start_at:
            time_str = talk.start_at.strftime("%H:%M")
        else:
            time_str = "время уточняется"

        if talk.speaker:
            speaker_name = (
                talk.speaker.first_name
                or talk.speaker.username
                or "спикер уточняется"
            )
        else:
            speaker_name = "спикер уточняется"

        lines.append(f"{idx}. {time_str} — {talk.title} ({speaker_name})")

    text = "\n".join(lines)

    update.message.reply_text(
        text,
        reply_markup=get_schedule_keyboard(),   # тут появляется кнопка "ФИО выступающих"
    )
