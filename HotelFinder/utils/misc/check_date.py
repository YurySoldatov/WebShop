from datetime import datetime


class Date:
    """
    Класс, содержащий методы преобразования формата
    даты из строки в словарь.
    """

    @classmethod
    def from_string(cls, date_str: str) -> dict:
        """
        Метод преобразования даты
        :param date_str: str
        :return: dict
        """
        if cls.is_date_valid(date_str):
            date_list = date_str.split('.')
            date_dict = dict()
            date_dict['day'] = int(date_list[0])
            date_dict['month'] = int(date_list[1])
            date_dict['year'] = int(date_list[2])
            date_dict['date'] = datetime(date_dict["year"], date_dict["month"], date_dict["day"])
            return date_dict
        else:
            raise ValueError('Некорректный ввод даты')

    @classmethod
    def is_date_valid(cls, date_str: str) -> bool:
        """
        Метод проверки корректности даты
        :param date_str: str
        :return: bool
        """
        try:
            date_list = date_str.split('.')
            day = int(date_list[0])
            month = int(date_list[1])
            year = int(date_list[2])
            day_correct = False
            month_correct = False
            year_correct = False
            year_is_vis = False

            if 0 <= year <= 9999:
                year_correct = True
                if year % 4 == 0 and year % 100 != 0:
                    year_is_vis = True
                elif year % 400 == 0:
                    year_is_vis = True
            if 1 <= month <= 12:
                month_correct = True
            if 1 <= day <= 28:
                day_correct = True
            elif (1 <= day <= 31) and (month in [1, 3, 5, 7, 8, 10, 12]):
                day_correct = True
            elif day == 29 and month == 2 and year_is_vis:
                day_correct = True

            if all([day_correct, month_correct, year_correct]):
                return True
            else:
                return False
        except (ValueError, IndexError, TypeError):
            return False
