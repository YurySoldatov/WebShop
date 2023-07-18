from requests import codes, get, post, Response


def request_to_api(method: str, url: str, headers: dict, params=None, json=None) -> Response:
    """
    Функция формирует api-запрос и возвращает ответ.
    :param method: (str) метод запроса: "GET" или "POST"
    :param url: (str) url-адрес
    :param headers: dict
    :param params: dict
    :param json: dict
    :return: Response
    """

    try:
        if method == "GET":
            if params:
                response = get(url=url, params=params, headers=headers, timeout=20)
            else:
                response = get(url=url, json=json, headers=headers, timeout=20)
            if response.status_code == codes.ok:
                return response

        elif method == "POST":
            if params:
                response = post(url=url, params=params, headers=headers, timeout=20)
            else:
                response = post(url=url, json=json, headers=headers, timeout=20)
            if response.status_code == codes.ok:
                return response

    except ConnectionError:
        raise ConnectionError('Ошибка соединения!')
