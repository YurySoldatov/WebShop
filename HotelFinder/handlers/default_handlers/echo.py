from telebot.types import Message

from loader import bot
from . import help


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """
    For unhandled messages
    :param message: Message
    :return: None
    """
    bot.reply_to(
        message, 'Я не знаю команду "{}"\nВот список моих команд:'.format(message.text)
    )
    help.bot_help(message)

