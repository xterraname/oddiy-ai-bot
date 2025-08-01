from peewee import SqliteDatabase
from config import DB_NAME

db = SqliteDatabase(DB_NAME)

def init_db():
    from .models import User, Chat, Message
    db.connect()
    db.create_tables([User, Chat, Message], safe=True)
