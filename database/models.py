from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    TextField,
    BooleanField,
    fn,
)
from .db import db


ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "asisstant"
ROLES = [ROLE_SYSTEM, ROLE_USER, ROLE_ASSISTANT]


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    telegram_id = IntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)

    def get_active_chat(self) -> "Chat":
        chat = Chat.select().where((Chat.user == self) & (Chat.is_active == True)).first()
        
        if not chat:
            chat = Chat.create(user=self)
        
        return chat


class Chat(BaseModel):
    id = IntegerField(primary_key=True)
    user = ForeignKeyField(User, backref="chats")

    is_active = BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            user = self.user
            Chat.update(is_active=False).where(
                (Chat.user == user) & (Chat.id != self.id)
            ).execute()

        return super().save(*args, **kwargs)

    def add_system_message(self, content: str) -> "Message":
        return Message.create(chat=self, role=ROLE_SYSTEM, content=content)

    def add_user_message(self, content: str) -> "Message":
        return Message.create(chat=self, role=ROLE_USER, content=content)

    def add_assistant_message(self, content: str) -> "Message":
        return Message.create(chat=self, role=ROLE_ASSISTANT, content=content)


class Message(BaseModel):
    id = IntegerField(primary_key=True)
    number = IntegerField()
    content = TextField()
    chat = ForeignKeyField(Chat, backref="messages")

    role = CharField(max_length=20)

    def save(self, *args, **kwargs):
        if self.role not in ROLES:
            raise ValueError(f"Role noto‘g‘ri: {self.role}")

        if not self.number:
            chat = self.chat

            last_number = (
                Message.select(fn.MAX(Message.number))
                .where(Message.chat == chat)
                .scalar()
            )
            self.number = (last_number or 0) + 1

        return super().save(*args, **kwargs)
