import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")
DB_PATH = "database/database.db"

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("lowprice", "Вывод самых дешёвых отелей в городе"),
    ("highprice", "Вывод самых дорогих отелей в городе"),
    ("bestdeal", "Вывод отелей, наиболее подходящих по цене и удалённости от центра"),
    ("history", "Вывод истории поиска отелей"),
)
