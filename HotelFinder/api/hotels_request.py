from datetime import datetime as dt
from peewee import InternalError

from config_data.config import RAPID_API_KEY, RAPID_API_HOST
from api.request_to_api import request_to_api
from api.request_details import request_details
from loader import bot
from database.models import HotelsRequests


def request_hotels(user_id: int) -> dict:
    """
    Функция для обработки второго запроса по отелям.
        Возвращает словарь, где ключ - имя отеля,
        значение - словарь с такими ключами -
        [id, адрес, расстояние от центра, цена, суммарная цена, рейтинг, ссылка]
    :param user_id: int
    :return: dict
    """

    with bot.retrieve_data(user_id) as hotels_data:
        url = "https://hotels4.p.rapidapi.com/properties/v2/list"

        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {"regionId": hotels_data['city_id']},
            "checkInDate": {
                "day": hotels_data['check_in_day'],
                "month": hotels_data['check_in_month'],
                "year": hotels_data['check_in_year']
            },
            "checkOutDate": {
                "day": hotels_data['check_out_day'],
                "month": hotels_data['check_out_month'],
                "year": hotels_data['check_out_year']
            },
            "rooms": [
                {
                    "adults": 1
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": hotels_data['num_hotels'] if not hotels_data["get_all"] else None,
            "sort": hotels_data['sort'],
            "filters": {"price": {
                "max": hotels_data['price_max'] if 'price_max' in hotels_data.keys() else None,
                "min": hotels_data['price_min'] if 'price_min' in hotels_data.keys() else None
            }}
        }

        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": RAPID_API_HOST
        }
        data = dict()

        try:
            response = request_to_api("POST", url, json=payload, headers=headers).json()
            if 'errors' in response.keys():
                raise ValueError('Упс! Что-то пошло не так.')

            if hotels_data["get_all"]:
                result = sorted(
                    response['data']['propertySearch']['properties'],
                    key=lambda elem: elem['price']['lead']['amount'],
                    reverse=True
                )
            else:
                result = response['data']['propertySearch']['properties']

            text = 'Найдены отели:'

            for i_hotel, hotel in enumerate(result):
                if i_hotel > hotels_data["num_hotels"]:
                    break
                name = hotel['name']
                price = round(hotel['price']['lead']['amount']) if 'price' in hotel.keys() else None
                total_days = dt.toordinal(hotels_data['check_out_date']) - dt.toordinal(hotels_data['check_in_date'])
                total_price = round(price * total_days) if isinstance(price, int) else None

                address, photos = request_details(hotel_id=hotel['id'])

                data[name] = {
                    'hotel_id': hotel['id'],
                    'address': address,
                    'distance': int(hotel['destinationInfo']['distanceFromDestination']['value']),
                    'total_days': total_days,
                    'price': price,
                    'total_price': total_price,
                    'rating': hotel['reviews']['score'] if 'reviews' in hotel.keys() else 'Нет',
                    'linc': f'https://www.hotels.com/h{hotel["id"]}.Hotel-Information',
                    'photos': photos
                }
                text += f'\n"{name}"'
            try:
                HotelsRequests.create(
                    user_id=user_id,
                    command=hotels_data["command"],
                    hotels=text
                )
            except InternalError as error:
                print(error)

            return data

        except (LookupError, TypeError, AttributeError):
            raise ValueError('Упс! Что-то пошло не так.')
