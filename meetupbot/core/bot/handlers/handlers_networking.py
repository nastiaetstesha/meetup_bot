from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from core.services.networking import save_profile, get_saved_profile
from core.services.networking_matching import get_other_profiles

PROFILE_FILL_NAME, PROFILE_FILL_AGE, PROFILE_FILL_STACK, PROFILE_FILL_GOAL, PROFILE_SHOW_MENU, MATCH_MENU = range(6)

exit_keyboard = ReplyKeyboardMarkup(
    [["Вернуться в меню"]],
    resize_keyboard=True
)

keyboard = ReplyKeyboardMarkup(
        [["Вернуться к анкете"], ["Вернуться в меню"]],
        resize_keyboard=True,
    )

def networking_start(update, context):
    text = update.message.text

    if text == "Вернуться к анкете":
        return return_profile_menu(update, context)

    if text == "Вернуться в меню":
        return _exit_to_menu(update)
    
    saved = get_saved_profile(update.effective_user)

    if saved:
        return return_profile_menu(update, context)

    context.user_data["profile"] = {}
    update.message.reply_text("Давай познакомимся 😊\n\nКак тебя зовут?", reply_markup=keyboard)
    return PROFILE_FILL_NAME


def profile_fill_name(update, context):
    text = update.message.text


    if text == "Вернуться к анкете":
        return return_profile_menu(update, context)

    if text == "Вернуться в меню":
        return _exit_to_menu(update)

    context.user_data["profile"]["name"] = update.message.text
    update.message.reply_text("Сколько тебе лет?", reply_markup=keyboard)
    return PROFILE_FILL_AGE


def profile_fill_age(update, context):
    text = update.message.text


    if text == "Вернуться к анкете":
        return return_profile_menu(update, context)

    if text == "Вернуться в меню":
        return _exit_to_menu(update)

    context.user_data["profile"]["age"] = update.message.text
    update.message.reply_text("Чем ты занимаешься (роль / стек)?", reply_markup=keyboard)
    return PROFILE_FILL_STACK


def profile_fill_stack(update, context):
    text = update.message.text


    if text == "Вернуться к анкете":
        return return_profile_menu(update, context)

    if text == "Вернуться в меню":
        return _exit_to_menu(update)

    context.user_data["profile"]["stack"] = update.message.text
    update.message.reply_text("Кого ты хочешь найти на митапе?", reply_markup=keyboard)
    return PROFILE_FILL_GOAL


def profile_fill_goal(update, context):
    text = update.message.text

    if text == "Вернуться к анкете":
        return return_profile_menu(update, context)

    if text == "Вернуться в меню":
        return _exit_to_menu(update)


    context.user_data["profile"]["goal"] = update.message.text
    save_profile(update.effective_user, context.user_data["profile"])

    return return_profile_menu(update, context)


def profile_menu_handler(update, context):
    text = update.message.text

    if text == "Искать собеседника":
        context.user_data["match_index"] = 0
        send_current_match(update, context)
        return MATCH_MENU

    if text == "Редактировать анкету":
        context.user_data["profile"] = {}
        update.message.reply_text("Как тебя зовут?", reply_markup=keyboard)
        return PROFILE_FILL_NAME

    if text == "Вернуться в меню":
        return _exit_to_menu(update)

    if text == "Вернуться к анкете":
        return return_profile_menu(update, context)

    update.message.reply_text("Выберите кнопку снизу.")
    return PROFILE_SHOW_MENU


def send_current_match(update, context):
    user_id = update.effective_user.id
    matches = get_other_profiles(user_id)

    idx = context.user_data.get("match_index", 0)

    if idx >= len(matches):
        keyboard = ReplyKeyboardMarkup(
            [["Вернуться к анкете"], ["Вернуться в меню"]],
            resize_keyboard=True,
        )
        update.message.reply_text("Анкеты других участников закончились 🙂", reply_markup=keyboard)
        return

    m = matches[idx]

    text = (
        f"Имя: {m.name}\n"
        f"Возраст: {m.age}\n"
        f"Занятие: {m.stack}\n"
        f"Ищу: {m.goal}\n\n"
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
    user_id = update.effective_user.id
    matches = get_other_profiles(user_id)
    idx = context.user_data.get("match_index", 0)

    if text == "Вернуться в меню":
        return _exit_to_menu(update)

    if text == "Вернуться к анкете":
        return return_profile_menu(update, context)

    if text == "Следующий собеседник":
        context.user_data["match_index"] = idx + 1
        return send_current_match(update, context) or MATCH_MENU

    if text == "Написать этому человеку":
        if idx < len(matches):
            m = matches[idx]
            username = m.user.username
            if username:
                update.message.reply_text(f"Напиши в личку: @{username}")
            else:
                update.message.reply_text("У пользователя не указан username.")

        return MATCH_MENU

    update.message.reply_text("Используйте кнопки ниже.")
    return MATCH_MENU



def return_profile_menu(update, context):
    saved = get_saved_profile(update.effective_user)

    if saved:
        profile = {
            "name": saved.name,
            "age": saved.age,
            "stack": saved.stack,
            "goal": saved.goal,
        }
    else:
        profile = context.user_data.get("profile", {})

    keyboard = ReplyKeyboardMarkup(
        [
            ["Искать собеседника"],
            ["Редактировать анкету"],
            ["Выйти в главное меню"],
        ],
        resize_keyboard=True,
    )

    text = (
        f"📋 Ваша анкета:\n\n"
        f"Имя: {profile['name']}\n"
        f"Возраст: {profile['age']}\n"
        f"Занятие: {profile['stack']}\n"
        f"Ищу: {profile['goal']}"
    )

    update.message.reply_text(text, reply_markup=keyboard)
    return PROFILE_SHOW_MENU


def _exit_to_menu(update):
    from core.bot.keyboards.main_menu import get_main_menu_keyboard

    update.message.reply_text(
        "Вы вернулись в главное меню 👋",
        reply_markup=get_main_menu_keyboard(is_speaker=False),
    )
    return ConversationHandler.END
