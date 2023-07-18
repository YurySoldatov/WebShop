
from telebot.handler_backends import State, StatesGroup


class RequestInfoStatesGroup(StatesGroup):
    search_city = State()
    city_id = State()
    num_hotels = State()
    show_photos = State()
    num_photos = State()
    price_min = State()
    price_max = State()
    distance = State()
    check_in = State()
    check_out = State()
