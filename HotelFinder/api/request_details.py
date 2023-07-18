from typing import Any

from api.request_to_api import request_to_api
from config_data.config import RAPID_API_KEY, RAPID_API_HOST


def request_details(hotel_id: int) -> tuple[Any, list[Any]]:
    """
    Функция формирует и обрабатывает третий запрос к фотографиям отеля и возвращает ссылки на них.
    :param hotel_id: int
    :return: tuple
    """

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": hotel_id
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }

    try:
        response = request_to_api("POST", url, json=payload, headers=headers).json()
        result = response['data']['propertyInfo']
        photos_list = list()
        for index in result['propertyGallery']['images']:
            base_url = index['image']['url']
            photos_list.append(base_url)

        address = result['summary']['location']['address']['addressLine']
        return address, photos_list
    except (LookupError, TypeError, AttributeError):
        raise ValueError('Упс! Что-то пошло не так(')
