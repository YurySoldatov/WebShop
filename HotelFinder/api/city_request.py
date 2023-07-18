from typing import List

from config_data.config import RAPID_API_KEY, RAPID_API_HOST
from api.request_to_api import request_to_api


def city_request(city_name: str) -> List:
    """
    Формирование и обработка первого запроса.
        Возвращает список подходящих локаций и их ID.
    :param city_name: str
    :return: list
    """

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {
        "q": city_name,
        "locale": "en_US",
        "langid": "1033",
        "siteid": "300000001"
    }
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }

    try:
        response = (request_to_api("GET", url, params=querystring, headers=headers)).json()

        if response['sr']:
            cities = list()
            for dest in response['sr']:
                cities.append({'city_name': dest['regionNames']['fullName'],
                               'destination_id': dest['gaiaId'] if 'gaiaId' in dest.keys() else dest['hotelId']
                               })
        else:
            raise PermissionError('К сожалению, такой город не найден.')

        return cities

    except (LookupError, TypeError, AttributeError):
        raise ValueError('Упс! Что-то пошло не так.')
