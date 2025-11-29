import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

logger = logging.getLogger(__name__)

# Состояния анкеты "Познакомиться"
PROFILE_FILL_NAME, PROFILE_FILL_AGE, PROFILE_FILL_STACK, PROFILE_FILL_GOAL, PROFILE_SHOW_MENU, MATCH_MENU = range(6)

# Кнопка выхода во время заполнения
exit_keyboard = ReplyKeyboardMarkup(
    [["Вернуться в меню"]],
    resize_keyboard=True
)

# Фейковые собеседники (заглушка)
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


# Основной сценарий "Познакомиться"

def networking_start(update, context):
    context.user_data["profile"] = {}
    update.message.reply_text(
        "Давай познакомимся 😊\n\nКак тебя зовут?",
        reply_markup=exit_keyboard
    )
    return PROFILE_FILL_NAME


def profile_fill_name(update, context):
    if update.message.text == "Вернуться в меню":
        return _exit_to_menu(update)

    context.user_data["profile"]["name"] = update.message.text
    update.message.reply_text("Сколько тебе лет?", reply_markup=exit_keyboard)
    return PROFILE_FILL_AGE


def profile_fill_age(update, context):
    if update.message.text == "Вернуться в меню":
        return _exit_to_menu(update)

    context.user_data["profile"]["age"] = update.message.text
    update.message.reply_text("Чем ты занимаешься? (роль / стек)", reply_markup=exit_keyboard)
    return PROFILE_FILL_STACK


def profile_fill_stack(update, context):
    if update.message.text == "Вернуться в меню":
        return _exit_to_menu(update)

    context.user_data["profile"]["stack"] = update.message.text
    update.message.reply_text("Кого ты хочешь найти на митапе?", reply_markup=exit_keyboard)
    return PROFILE_FILL_GOAL


def profile_fill_goal(update, context):
    if update.message.text == "Вернуться в меню":
        return _exit_to_menu(update)

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
        context.user_data["match_index"] = 0
        send_current_match(update, context)
        return MATCH_MENU

    if text == "Редактировать анкету":
        context.user_data["profile"] = {}
        update.message.reply_text(
            "Окей, заполним анкету заново 🙂\n\nКак тебя зовут?",
            reply_markup=exit_keyboard
        )
        return PROFILE_FILL_NAME

    if text == "Выйти в главное меню":
        return _exit_to_menu(update)

    update.message.reply_text("Выберите кнопку снизу 🙂")
    return PROFILE_SHOW_MENU


# Поиск собеседника

def send_current_match(update, context):
    idx = context.user_data.get("match_index", 0)

    if idx >= len(FAKE_MATCHES):
        keyboard = ReplyKeyboardMarkup(
            [
                ["Вернуться к анкете"],
                ["Выйти в меню"],
            ],
            resize_keyboard=True,
        )
        update.message.reply_text(
            "Анкеты закончились 🙂",
            reply_markup=keyboard
        )
        return

    m = FAKE_MATCHES[idx]

    text = (
        "Вот один из участников 👇\n\n"
        f"Имя: {m['name']}\n"
        f"Возраст: {m['age']}\n"
        f"Занятие: {m['stack']}\n"
        f"Ищу: {m['goal']}\n\n"
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

    if text == "Вернуться в меню":
        return _exit_to_menu(update)

    if text == "Написать этому человеку":
        m = FAKE_MATCHES[idx]
        update.message.reply_text(f"Напиши в личку: {m['username']}")
        return MATCH_MENU

    if text == "Следующий собеседник":
        context.user_data["match_index"] = idx + 1
        send_current_match(update, context)
        return MATCH_MENU

    if text == "Вернуться к анкете":
        profile = context.user_data["profile"]
        keyboard = ReplyKeyboardMarkup(
            [
                ["Искать собеседника"],
                ["Редактировать анкету"],
                ["Выйти в главное меню"],
            ],
            resize_keyboard=True,
        )
        update.message.reply_text(
            f"📋 Ваша анкета:\n\n"
            f"Имя: {profile['name']}\n"
            f"Возраст: {profile['age']}\n"
            f"Занятие: {profile['stack']}\n"
            f"Ищу: {profile['goal']}",
            reply_markup=keyboard
        )
        return PROFILE_SHOW_MENU

    update.message.reply_text("Выберите действие по кнопкам ниже.")
    return MATCH_MENU

# Выход в меню

def _exit_to_menu(update):
    from core.bot.keyboards.main_menu import get_main_menu_keyboard
    update.message.reply_text(
        "Вы вернулись в главное меню 👋",
        reply_markup=get_main_menu_keyboard(is_speaker=False),
    )
    return ConversationHandler.END
