from decimal import Decimal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup

from core.models import TelegramUser, Event
from core.services.donations import create_pending_donation, mark_donation_paid


ASK_AMOUNT = 1
PROFILE_FILL_NAME, PROFILE_FILL_AGE, PROFILE_FILL_STACK, PROFILE_FILL_GOAL, PROFILE_SHOW_MENU, MATCH_MENU= range(6)

# Клавиатура для выхода во время заполнения анкеты
exit_keyboard = ReplyKeyboardMarkup(
    [["Вернуться в меню"]],
    resize_keyboard=True
)

# Фейковые анкеты собеседников (заглушка вместо БД)
FAKE_MATCHES = [
    {
        "name": "Аня",
        "age": "23",
        "stack": "Python junior",
        "goal": "найти людей для pet-проекта",
        "username": "@anya_python",
    },
    {
        "name": "Игорь",
        "age": "27",
        "stack": "Data analyst",
        "goal": "пообщаться про карьеру в аналитике",
        "username": "@igor_data",
    },
    {
        "name": "Лена",
        "age": "30",
        "stack": "QA engineer",
        "goal": "найти разработчиков для совместного обучения",
        "username": "@lena_qa",
    },
]


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


#Кнопки для "Познакомиться"

def networking_start(update, context):
    context.user_data["profile"] = {}

    update.message.reply_text(
        "Давай познакомимся 😊\n\nКак тебя зовут?",
        reply_markup=exit_keyboard
    )
    return PROFILE_FILL_NAME


def profile_fill_name(update, context):
    # Кнопка выхода в меню
    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    context.user_data["profile"]["name"] = update.message.text
    update.message.reply_text("Сколько тебе лет?", reply_markup=exit_keyboard)
    return PROFILE_FILL_AGE


def profile_fill_age(update, context):
    # Кнопка выхода в меню
    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    context.user_data["profile"]["age"] = update.message.text
    update.message.reply_text("Чем ты занимаешься? (роль / стек)", reply_markup=exit_keyboard)
    return PROFILE_FILL_STACK


def profile_fill_stack(update, context):
    # Кнопка выхода в меню
    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    context.user_data["profile"]["stack"] = update.message.text
    update.message.reply_text("Кого ты хочешь найти на митапе?", reply_markup=exit_keyboard)
    return PROFILE_FILL_GOAL


def profile_fill_goal(update, context):
    if update.message.text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    context.user_data["profile"]["goal"] = update.message.text
    profile = context.user_data["profile"]

    text = (
        "📋 Ваша анкета:\n\n"
        f"Имя: {profile['name']}\n"
        f"Возраст: {profile['age']}\n"
        f"Занятие: {profile['stack']}\n"
        f"Ищу: {profile['goal']}\n\n"
        "Готовы найти собеседника?"
    )

    keyboard = ReplyKeyboardMarkup(
        [
            ["Искать собеседника"],
            ["Редактировать анкету"],
            ["Выйти в главное меню"],
        ],
        resize_keyboard=True
    )

    update.message.reply_text(text, reply_markup=keyboard)
    return PROFILE_SHOW_MENU



def profile_menu_handler(update, context):
    text = update.message.text

    if text == "Искать собеседника":
        # начинаем с первого собеседника
        context.user_data["match_index"] = 0
        send_current_match(update, context)
        return MATCH_MENU

    if text == "Редактировать анкету":
        # очищаем предыдущие данные
        context.user_data["profile"] = {}
        # снова начинаем с первого вопроса и показываем клавиатуру выхода
        update.message.reply_text(
            "Окей, заполним анкету заново 🙂\n\nКак тебя зовут?",
            reply_markup=exit_keyboard
        )
        return PROFILE_FILL_NAME

    if text == "Выйти в главное меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    # если пришёл какой-то другой текст
    update.message.reply_text("Пожалуйста, выберите вариант с клавиатуры.")
    return PROFILE_SHOW_MENU

#Кнопки для "Поиска собеседника"
def send_current_match(update, context):
    """Показать текущего собеседника по индексу из user_data."""
    matches = FAKE_MATCHES
    idx = context.user_data.get("match_index", 0)

    if not matches:
        # На всякий случай, если список пустой
        update.message.reply_text(
            "Пока нет анкет других участников.\n"
            "Попробуй чуть позже 🙂"
        )
        return

    if idx >= len(matches):
        # Больше анкет нет
        keyboard = ReplyKeyboardMarkup(
            [
                ["Вернуться к анкете"],
                ["Выйти в меню"],
            ],
            resize_keyboard=True,
        )
        update.message.reply_text(
            "На данный момент больше нет анкет.\n"
            "Можешь вернуться к своей анкете или в главное меню.",
            reply_markup=keyboard,
        )
        return

    m = matches[idx]
    text = (
        "Вот один из участников 👇\n\n"
        f"Имя: {m['name']}\n"
        f"Возраст: {m['age']}\n"
        f"Занятие: {m['stack']}\n"
        f"Ищет: {m['goal']}\n\n"
        f"Telegram: {m['username']}"
    )

    keyboard = ReplyKeyboardMarkup(
        [
            ["Написать этому человеку"],
            ["Следующий собеседник"],
            ["Вернуться к анкете"],
        ],
        resize_keyboard=True,
    )

    update.message.reply_text(text, reply_markup=keyboard)


def match_menu_handler(update, context):
    text = update.message.text
    idx = context.user_data.get("match_index", 0)

    # Поддержка аварийного выхода "Вернуться в меню"
    if text == "Вернуться в меню":
        from core.bot.keyboards.main_menu import get_main_menu_keyboard
        update.message.reply_text(
            "Вы вернулись в главное меню 👋",
            reply_markup=get_main_menu_keyboard(is_speaker=False)
        )
        return ConversationHandler.END

    if text == "Написать этому человеку":
        # Берём текущего собеседника
        if 0 <= idx < len(FAKE_MATCHES):
            m = FAKE_MATCHES[idx]
            update.message.reply_text(
                f"Напиши этому человеку в личку: {m['username']} 🙂"
            )
        else:
            update.message.reply_text(
                "Не удалось найти данные собеседника. Попробуй переключить анкету."
            )
        # Остаёмся в том же состоянии
        return MATCH_MENU

    if text == "Следующий собеседник":
        # Переходим к следующему
        idx += 1
        context.user_data["match_index"] = idx
        send_current_match(update, context)
        return MATCH_MENU

    if text == "Вернуться к анкете":
        profile = context.user_data.get("profile", {})
        from core.bot.keyboards.main_menu import get_main_menu_keyboard  # если нужно

        text_profile = (
            "📋 Ваша анкета:\n\n"
            f"Имя: {profile.get('name', '-')}\n"
            f"Возраст: {profile.get('age', '-')}\n"
            f"Занятие: {profile.get('stack', '-')}\n"
            f"Ищу: {profile.get('goal', '-')}\n\n"
            "Что хотите сделать дальше?"
        )

        keyboard = ReplyKeyboardMarkup(
            [
                ["Искать собеседника"],
                ["Редактировать анкету"],
                ["Выйти в главное меню"],
            ],
            resize_keyboard=True,
        )

        update.message.reply_text(text_profile, reply_markup=keyboard)
        return PROFILE_SHOW_MENU

    # Любой другой текст
    update.message.reply_text("Пожалуйста, используйте кнопки ниже 🙂")
    return MATCH_MENU