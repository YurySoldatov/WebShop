from loader import bot
from telebot.types import Message, CallbackQuery
from datetime import datetime
from random import choice

from states.info_for_request import RequestInfoStatesGroup
from api.city_request import city_request
from api.hotels_request import request_hotels
from keyboards.inline.choice_yes_no import yes_no_keyboard
from keyboards.inline.cities_list import city_markup
from utils.misc.check_date import Date


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """
    Обработчик команды "lowprice".
        Начало сценария сбора информации для запроса списка дешёвых отелей.
        Передаёт эстафету состояний на запрос города у пользователя.
    :param message: Message
    :return: None
    """

    bot.send_message(message.from_user.id, 'Ищем самые дешёвые отели')
    bot.set_state(message.from_user.id, RequestInfoStatesGroup.search_city, message.chat.id)
    bot.send_message(message.from_user.id, 'В каком городе будем искать (латиницей)?')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = "/lowprice"
        data["sort"] = "PRICE_LOW_TO_HIGH"
        data["get_all"] = False
        data["price_min"] = None
        data["price_max"] = None


@bot.message_handler(commands=['highprice'])
def highprice(message: Message) -> None:
    """
    Обработчик команды "highprice".
        Начало сценария сбора информации для запроса списка дорогих отелей.
        Передаёт эстафету состояний на запрос города у пользователя.
        :param message: Message
    :return: None
    """

    bot.send_message(message.from_user.id, 'Ищем самые дорогие отели')
    bot.set_state(message.from_user.id, RequestInfoStatesGroup.search_city, message.chat.id)
    bot.send_message(message.from_user.id, 'В каком городе будем искать (латиницей)?')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = "/highprice"
        data["sort"] = "DISTANSE"
        data["get_all"] = True
        data["price_min"] = None
        data["price_max"] = None


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message: Message) -> None:
    """
    Обработчик команды "bestdeal".
        Начало сценария сбора информации для запроса списка подходящих отелей.
        Передаёт эстафету состояний на запрос у пользователя минимальной цены номера.
    :param message: Message
    :return: None
    """

    bot.send_message(message.from_user.id, 'Ищем самые подходящие отели')
    bot.set_state(message.from_user.id, RequestInfoStatesGroup.price_min, message.chat.id)
    bot.send_message(message.from_user.id, 'В каком ценовом сегменте будем искать?')
    bot.send_message(message.from_user.id, 'min($): ')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = "/bestdeal"
        data["sort"] = "DISTANCE"
        data["get_all"] = False


@bot.message_handler(state=RequestInfoStatesGroup.price_min)
def set_price_min(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет информацию о минимальной цене номера.
        Передаёт эстафету состояний на запрос у пользователя максимальной цены номера.
    :param message: Message
    :return: None
    """
    if message.text.isnumeric():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["price_min"] = int(message.text)

        bot.set_state(message.from_user.id, RequestInfoStatesGroup.price_max, message.chat.id)
        bot.send_message(message.from_user.id, 'max($): ')

    else:
        bot.send_message(message.from_user.id, 'Некорректный ввод\nПопробуйте ещё раз')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.price_min, message.chat.id)


@bot.message_handler(state=RequestInfoStatesGroup.price_max)
def set_price_max(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет информацию о максимальной цене номера.
        Передаёт эстафету состояний на запрос у пользователя максимальной удалённости отеля от центра города.
    :param message: Message
    :return: None
    """

    if message.text.isnumeric():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["price_max"] = int(message.text)

        bot.set_state(message.from_user.id, RequestInfoStatesGroup.distance, message.chat.id)
        bot.send_message(message.from_user.id, 'В каком радиусе от центра (в метрах)?')

    else:
        bot.send_message(message.from_user.id, 'Некорректный ввод\nПопробуйте ещё раз')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.price_max, message.chat.id)


@bot.message_handler(state=RequestInfoStatesGroup.distance)
def set_distance(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет информацию о максимальной удалённости отеля от центра города.
        Передаёт эстафету состояний на запрос города у пользователя.
    :param message: Message
    :return: None
    """

    bot.set_state(message.from_user.id, RequestInfoStatesGroup.search_city, message.chat.id)
    bot.send_message(message.from_user.id, 'В каком городе ищем (латиницей)?')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["distance"] = message.text


@bot.message_handler(state=RequestInfoStatesGroup.search_city)
def set_search_city(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет название города, введённое пользователем.
        Формирует первичный api-запрос с названием города.
        Выводит для уточнения список городов, удовлетворяющих запросу, в виде inline-клавиатуры.
        Передаёт эстафету состояний на обработчик inline-кнопок.
    :param message: Message
    :return: None
    """

    try:
        answer = city_request(message.text.lower())
    except (PermissionError, ConnectionError, ValueError) as error:
        bot.send_message(message.from_user.id, error)
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.search_city)
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["search_city"] = message.text

        bot.send_message(message.from_user.id, 'Уточни, пожалуйста:', reply_markup=city_markup(answer))
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.city_id, message.chat.id)


@bot.callback_query_handler(func=None, state=RequestInfoStatesGroup.city_id)
def check_city(call: CallbackQuery) -> None:
    """
    Обработчик inline кнопок.
        Сохраняет id города.
        Передаёт эстафету состояний на запрос у пользователя количества отелей в выводимом списке.
    :param call: CallbackQuery
    :return: None
    """

    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        data['city_id'] = call.data

    bot.send_message(call.from_user.id, 'Понял!')
    bot.send_message(call.from_user.id, 'Какое количество отелей показываем?')
    bot.set_state(call.from_user.id, RequestInfoStatesGroup.num_hotels)


@bot.message_handler(state=RequestInfoStatesGroup.num_hotels)
def set_num_hotels(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет информацию о количестве отелей в выводимом списке.
        Передаёт эстафету состояний на запрос у пользователя необходимости загрузки фотографий.
    :param message: Message
    :return: None
    """

    if message.text.isnumeric():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["num_hotels"] = int(message.text)

        bot.send_message(message.from_user.id, 'Фотографии нужны?', reply_markup=yes_no_keyboard())
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.show_photos, message.chat.id)

    else:
        bot.send_message(message.from_user.id, 'Введите ЧИСЛО отелей в списке')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.num_hotels)


@bot.callback_query_handler(func=None, state=RequestInfoStatesGroup.show_photos)
def set_show_photos(call: CallbackQuery) -> None:
    """
    Обработчик inline кнопок.
        Сохраняет информацию о необходимости загрузки фотографий.
        В зависимости от выбора пользователя,
        передаёт эстафету состояний на запрос у пользователя количества загружаемых фотографий,
        либо на формирование api-запроса.
    :param call: CallbackQuery
    :return: None
    """

    if call.data == "True":
        bot.send_message(call.from_user.id, 'По сколько шт.(не больше 10)?')
        bot.set_state(call.from_user.id, RequestInfoStatesGroup.num_photos)

    else:
        bot.send_message(call.from_user.id, 'Дата въезда (ДД.ММ.ГГГГ):')
        bot.set_state(call.from_user.id, RequestInfoStatesGroup.check_in)

        with bot.retrieve_data(call.from_user.id) as data:
            data["num_photos"] = 0


@bot.message_handler(state=RequestInfoStatesGroup.num_photos)
def set_num_photos(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет информацию о количестве загружаемых фотографий.
        Передаёт эстафету состояний на запрос у пользователя даты въезда.
    :param message: Message
    :return: None
    """

    if message.text.isnumeric() and (0 < int(message.text) <= 10):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["num_photos"] = int(message.text)

        bot.send_message(message.from_user.id, 'Дата въезда (ДД.ММ.ГГГГ):')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.check_in)

    else:
        bot.send_message(message.from_user.id, 'Некорректный ввод!')
        bot.send_message(message.from_user.id, 'Введите количество фотографий (не больше 10)')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.num_photos)


@bot.message_handler(state=RequestInfoStatesGroup.check_in)
def set_check_in(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет информацию о дате въезда.
        Передаёт эстафету состояний на запрос у пользователя даты выезда.
    :param message: Message
    :return: None
    """

    try:
        date_in = Date.from_string(message.text)
        if date_in["date"] < datetime.now():
            raise ValueError('Дата въезда не может быть раньше, чем сегодня')
    except ValueError as error:
        bot.send_message(message.from_user.id, error)
        bot.send_message(message.from_user.id, 'Попробуте ещё раз')
        bot.send_message(message.from_user.id, 'Дата въезда (ДД.ММ.ГГГГ):')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.check_in)
    else:
        bot.send_message(message.from_user.id, 'Дата выезда (ДД.ММ.ГГГГ):')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.check_out)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["check_in_day"] = date_in["day"]
            data["check_in_month"] = date_in["month"]
            data["check_in_year"] = date_in["year"]
            data["check_in_date"] = date_in["date"]


@bot.message_handler(state=RequestInfoStatesGroup.check_out)
def set_check_out(message: Message) -> None:
    """
    Обработчик сообщения.
        Сохраняет информацию о дате выезда.
        Формирует и отправляет запрос, выводит обработанный ответ.
    :param message: Message
    :return: None
    """

    try:
        date_out = Date.from_string(message.text)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if date_out["date"] < data["check_in_date"]:
                raise ValueError('Дата выезда не может быть раньше, чем дата въезда')

    except ValueError as error:
        bot.send_message(message.from_user.id, error)
        bot.send_message(message.from_user.id, 'Попробуте ещё раз')
        bot.send_message(message.from_user.id, 'Дата выезда (ДД.ММ.ГГГГ):')
        bot.set_state(message.from_user.id, RequestInfoStatesGroup.check_out)
    else:
        bot.send_message(message.from_user.id, 'Ок, ищем...')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["check_out_day"] = date_out["day"]
            data["check_out_month"] = date_out["month"]
            data["check_out_year"] = date_out["year"]
            data["check_out_date"] = date_out["date"]
            num = data["num_photos"]

        get_result(message.from_user.id, num)
        bot.delete_state(message.from_user.id)


def get_result(user_id: int, num_photos: int):
    """
    Запрос отелей и вывод результатов.
    :param user_id: int
    :param num_photos: int
    :return: None
    """

    try:
        hotels = request_hotels(user_id)
    except (ValueError, ConnectionError) as error:
        bot.send_message(user_id, error)
    else:
        for name, hotel in hotels.items():
            bot.send_message(
                user_id,
                '"{name}"\n'
                'Цена за сутки: ${price}\n'
                'Общая стоимость: ${total_price}\n'
                'Рейтинг: {rating}\n'
                'Адрес: {address}\n'
                'Расстояние до центра: {distance}\n'
                '{linc}'.format(
                    name=name,
                    price=hotel["price"],
                    total_price=hotel["total_price"],
                    rating=hotel["rating"],
                    address=hotel["address"],
                    distance=hotel["distance"],
                    linc=hotel["linc"]
                )
            )
            for _ in range(num_photos):
                bot.send_photo(user_id, choice(hotel["photos"]))


