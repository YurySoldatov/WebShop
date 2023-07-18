from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def yes_no_keyboard() -> InlineKeyboardMarkup:
    """
    Inline-клавиатура.
        Две кнопки: "Да" и "Нет".
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup()
    btn_1 = InlineKeyboardButton(text='Да', callback_data="True")
    keyboard.add(btn_1)
    btn_2 = InlineKeyboardButton(text='Нет', callback_data="False")
    keyboard.add(btn_2)
    return keyboard
