from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters
from django.utils import timezone

from core.models import Event, Talk, TelegramUser, Question
from core.bot.keyboards.main_menu import get_main_menu_keyboard, get_speaker_menu_keyboard

CHOOSE_TALK, WRITE_QUESTION = range(2)


def _get_current_event():
    now = timezone.now().date()
    event = Event.objects.filter(is_current=True).order_by("date").first()
    if event:
        return event
    return (
        Event.objects.filter(is_active=True, date__gte=now)
        .order_by("date")
        .first()
    )


# слушатель: задать вопрос 


def ask_question_entry(update: Update, context: CallbackContext):
    event = _get_current_event()
    if not event:
        update.message.reply_text(
            "Сейчас нет активного мероприятия, задавать вопросы некому"
        )
        return ConversationHandler.END

    talks = event.talks.all().order_by("start_at", "order")
    if not talks.exists():
        update.message.reply_text(
            "Программа докладов ещё формируется, поэтому пока некому задать вопрос"
        )
        return ConversationHandler.END

    # делаем клавиатуру с названиями докладов
    from telegram import ReplyKeyboardMarkup

    titles = [[talk.title] for talk in talks]
    context.user_data["talks_map"] = {talk.title: talk.id for talk in talks}

    update.message.reply_text(
        "Выбери доклад, к которому хочешь задать вопрос:",
        reply_markup=ReplyKeyboardMarkup(titles + [["⬅️ Назад"]], resize_keyboard=True),
    )
    return CHOOSE_TALK


def ask_question_choose_talk(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if text in ("⬅️ Назад", "Назад"):
        update.message.reply_text("Окей, вернёмся в меню")
        return ConversationHandler.END

    talks_map = context.user_data.get("talks_map") or {}
    talk_id = talks_map.get(text)
    if not talk_id:
        update.message.reply_text("Пожалуйста, выбери доклад из списка.")
        return CHOOSE_TALK

    context.user_data["question_talk_id"] = talk_id

    update.message.reply_text(
        "Напиши свой вопрос, я передам его спикеру:",
        reply_markup=get_cancel_keyboard(),
    )
    return WRITE_QUESTION


def ask_question_write(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if text in ("⬅️ Назад", "Назад"):
        update.message.reply_text("Окей, вернёмся в меню")
        return ConversationHandler.END

    tg_user = update.effective_user
    db_user, _ = TelegramUser.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={"username": tg_user.username or ""},
    )

    talk_id = context.user_data.get("question_talk_id")
    talk = Talk.objects.filter(id=talk_id).select_related("event", "speaker").first()
    if not talk:
        update.message.reply_text("Не смог найти доклад, попробуй ещё раз ")
        return ConversationHandler.END

    question = Question.objects.create(
        event=talk.event,
        talk=talk,
        author=db_user,
        text=text,
        is_answered=False,
    )

    # уведомляем спикера, если он есть
    speaker = talk.speaker
    if speaker and speaker.tg_id:
        update.bot.send_message(
            chat_id=speaker.tg_id,
            text=(
                f"Новый вопрос к твоему докладу «{talk.title}»:\n\n"
                f"{text}"
            ),
        )

    update.message.reply_text(
        "Спасибо! Я передал твой вопрос спикеру"
    )
    return ConversationHandler.END


# спикерский режим: кнопка "Я спикер"


# def enter_speaker_mode(update: Update, context: CallbackContext):
#     tg_user = update.effective_user
#     db_user, _ = TelegramUser.objects.get_or_create(
#         tg_id=tg_user.id,
#         defaults={"username": tg_user.username or ""},
#     )

#     # ищем доклады этого пользователя
#     event = _get_current_event()
#     talk = (
#         Talk.objects.filter(event=event, speaker=db_user, is_current=True)
#         .order_by("start_at")
#         .first()
#     )

#     if not event or not talk:
#         update.message.reply_text(
#             "Я не вижу твоего выступления в сегодняшней программе \n"
#             "Если хочешь подать заявку, нажми «Хочу быть спикером»."
#         )
#         return

#     # помечаем, что он спикер 
#     db_user.is_speaker = True
#     db_user.save()

#     context.user_data["speaker_mode"] = True
#     context.user_data["current_talk_id"] = talk.id

#     update.message.reply_text(
#         "Отлично! Я запомнил, что ты спикер.\n"
#         "Теперь можешь смотреть вопросы слушателей к твоему выступлению.",
#         reply_markup=get_speaker_menu_keyboard(),
#     )
def enter_speaker_mode(update: Update, context: CallbackContext):
    tg_user = update.effective_user

    db_user, _ = TelegramUser.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={"username": tg_user.username or ""},
    )

    # 1. Сначала ищем доклад по tg-пользователю и флагу is_current
    talk = (
        Talk.objects.filter(speaker=db_user, is_current=True)
        .select_related("event")
        .order_by("start_at")
        .first()
    )

    # 2. Если не нашли — пробуем по username (на случай «ручного» TelegramUser)
    if not talk and tg_user.username:
        talk = (
            Talk.objects.filter(
                speaker__username=tg_user.username,
                is_current=True,
            )
            .select_related("event", "speaker")
            .order_by("start_at")
            .first()
        )

        # если нашли по username, но speaker другой объект —
        # перепривяжем доклад к "правильному" db_user
        if talk and talk.speaker != db_user:
            old_speaker = talk.speaker
            talk.speaker = db_user
            talk.save()
            # опционально: старого можно почистить руками в админке

    if not talk:
        update.message.reply_text(
            "Я не вижу твое выступление в сегодняшней программе \n"
            "Проверь, что в админке у доклада стоит галочка «Is current» "
            "и указан правильный спикер."
        )
        return

    # пометили, что пользователь сейчас спикер
    db_user.is_speaker = True
    db_user.save()

    context.user_data["speaker_mode"] = True
    context.user_data["current_talk_id"] = talk.id

    update.message.reply_text(
        f"Окей! Я запомнил, что ты сейчас выступаешь с докладом:\n"
        f"«{talk.title}»",
        reply_markup=get_speaker_menu_keyboard(),
    )

def _get_db_user(update: Update) -> TelegramUser:
    tg_user = update.effective_user
    db_user, _ = TelegramUser.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={"username": tg_user.username or ""},
    )
    return db_user


def _get_current_talk_for_speaker(db_user: TelegramUser, context: CallbackContext):
    """Пытаемся найти 'актуальный' доклад для спикера."""
    from core.models import Talk

    # 1) если мы его уже сохраняли при 'Я спикер'
    talk_id = context.user_data.get("current_talk_id")
    if talk_id:
        talk = Talk.objects.filter(id=talk_id).select_related("event").first()
        if talk:
            return talk

    # 2) иначе ищем по speaker + is_current
    talk = (
        Talk.objects.filter(speaker=db_user, is_current=True)
        .select_related("event")
        .order_by("start_at")
        .first()
    )
    return talk


def show_speaker_questions(update: Update, context: CallbackContext):
    """
    Кнопка 'Вопросы' в меню спикера.
    Показывает все вопросы к его текущему докладу.
    """
    db_user = _get_db_user(update)
    talk = _get_current_talk_for_speaker(db_user, context)

    if not talk:
        update.message.reply_text(
            "Я не нашёл актуального доклада, к которому можно показать вопросы \n"
            "Убедись, что у нужного Talk в админке стоит галочка 'Is current'."
        )
        return

    questions = Question.objects.filter(talk=talk).order_by("created_at")

    if not questions.exists():
        update.message.reply_text(
            f"К докладу «{talk.title}» пока нет вопросов ",
            reply_markup=get_speaker_menu_keyboard(),
        )
        return

    lines = [
        f"Вопросы к докладу «{talk.title}»:",
        "",
    ]
    for idx, q in enumerate(questions, start=1):
        author = q.author.username or q.author.tg_id if q.author else "аноним"
        lines.append(f"{idx}. {q.text}  (от {author})")

    text = "\n".join(lines)

    update.message.reply_text(
        text,
        reply_markup=get_speaker_menu_keyboard(),
    )


def speaker_still_talking(update: Update, context: CallbackContext):
    """
    Кнопка 'Еще выступаю' — просто поддерживающее сообщение.
    """
    db_user = _get_db_user(update)
    talk = _get_current_talk_for_speaker(db_user, context)

    if not talk:
        update.message.reply_text(
            "Я пока не вижу твоего активного доклада, но окей, продолжаем 🙂"
        )
        return

    update.message.reply_text(
        f"Окей! Продолжаем выступление с докладом «{talk.title}».\n"
        f"Можешь в любой момент нажать 'Вопросы', чтобы посмотреть вопросы, "
        f"или 'Выступил', когда закончишь.",
        reply_markup=get_speaker_menu_keyboard(),
    )


def speaker_finished(update: Update, context: CallbackContext):
    """
    Кнопка 'Выступил' — доклад завершён.
    Снимаем флаги и возвращаем в обычное меню.
    """
    db_user = _get_db_user(update)
    talk = _get_current_talk_for_speaker(db_user, context)

    if talk:
        talk.is_current = False
        talk.save()

    # если используешь is_speaker как флаг роли — снимаем
    if hasattr(db_user, "is_speaker"):
        db_user.is_speaker = False
        db_user.save()

    # чистим временные данные в user_data
    context.user_data.pop("speaker_mode", None)
    context.user_data.pop("current_talk_id", None)

    update.message.reply_text(
        "Спасибо за выступление! \n"
        "Я больше не отмечаю тебя как текущего спикера.\n"
        "Если будешь снова выступать — нажми «Я спикер».",
        reply_markup=get_main_menu_keyboard(is_speaker=False),
    )
