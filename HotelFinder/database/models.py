from datetime import datetime
from peewee import (
    TextField,
    CharField,
    DateField,
    IntegerField,
    Model,
    SqliteDatabase,
)
from config_data.config import DB_PATH

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class HotelsRequests(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    command = CharField(max_length=10)
    date_time = DateField(default=datetime.now())
    hotels = TextField()


def create_models():
    db.create_tables(BaseModel.__subclasses__())
