from loader import bot
from telebot.types import Message
from database.models import HotelsRequests


@bot.message_handler(commands=['history'])
def get_history(message: Message) -> None:
    requests_history = HotelsRequests.get_or_none(
        HotelsRequests.user_id == message.from_user.id,
    )
    if requests_history:
        text = ''
        queryset = HotelsRequests.select().where(HotelsRequests.user_id == message.from_user.id)
        for row in queryset:
            text += '{date_time}\n{command}\n{hotels}'.format(
                date_time=row.date_time,
                command=row.command,
                hotels=row.hotels
            )
        bot.send_message(message.from_user.id, text)
    else:
        bot.send_message(message.from_user.id, "История запросов пуста")
