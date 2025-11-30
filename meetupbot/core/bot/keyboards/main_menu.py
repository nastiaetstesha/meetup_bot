from telegram import ReplyKeyboardMarkup

DONATE_SUMS = [100, 200, 500, 1000]
BACK_BUTTON = "⬅️ Назад"

def get_main_menu_keyboard(is_speaker=False):
    """
    Основое меню
    Для спикера добавляет отдельный ряд с кнопками функций спикера.
    """
    buttons = [
        ["Афиша на сегодня", "Хочу быть спикером"],
        ["Познакомиться", "Донат"],
        ["Записаться на следующее мероприятие"],
        ["Задать вопрос", "Я спикер"],
    ]

    if is_speaker:
        buttons.append(["Вопросы", "Выступил"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

def get_donate_keyboard():
    return ReplyKeyboardMarkup(
        [[f"{amount} ₽" for amount in DONATE_SUMS], [BACK_BUTTON]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_donate_confirm_keyboard(amount):
    return ReplyKeyboardMarkup(
        [[f"{amount} ₽"], [BACK_BUTTON]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        [[BACK_BUTTON]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_next_profile_keyboard():
    return ReplyKeyboardMarkup(
        [["Посмотреть другого"], [" Начать сначала", "В меню"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_profiles_finished_keyboard():
    return ReplyKeyboardMarkup(
        [[" Начать сначала", "В меню"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_speakers_keyboard(speakers):
    return ReplyKeyboardMarkup(
        [[speaker["name"]] for speaker in speakers] + [["Назад"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

# def get_schedule_keyboard():
#     return ReplyKeyboardMarkup(
#         [[BACK_BUTTON]],
#         resize_keyboard=True,
#         one_time_keyboard=True,
# )
def get_speaker_keyboard():
    return ReplyKeyboardMarkup(
        [["Назад"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_speaker_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Еще выступаю", "Выступил"],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def get_speaker_menu_speech_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Вопросы", "Выступил"],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

def get_subscribe_keyboard(is_subscribed: bool = False):
 
    if is_subscribed:
        buttons = [["Не хочу следить за следующими мероприятиями", BACK_BUTTON]]
    else:
        buttons = [["Хочу следить за следующими мероприятиями", BACK_BUTTON]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)


def get_schedule_keyboard():
    return ReplyKeyboardMarkup(
        [["ФИО выступающих"], [BACK_BUTTON]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
