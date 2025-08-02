from typing import List
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
from prompts import SYSTEM_PROMPT

ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_TOOL = "tool"
ROLES = [ROLE_SYSTEM, ROLE_USER, ROLE_ASSISTANT, ROLE_TOOL]

MAX_CHAT_COUNT = 20


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    telegram_id = IntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)

    def get_active_chat(self) -> "Chat":
        chat = (
            Chat.select().where((Chat.user == self) & (Chat.is_active == True)).first()
        )

        if not chat:
            chat = Chat.create(user=self)
            chat.add_system_message()

        return chat

    @property 
    def number_chats(self) -> int:
        return self.chats.count()

    @property
    def number_chats_left(self) -> int:
        return max(MAX_CHAT_COUNT - self.number_chats, 0)


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

    def inactive(self):
        self.is_active = False
        self.save()

    def add_system_message(self) -> "Message":
        content = SYSTEM_PROMPT
        return Message.create(chat=self, role=ROLE_SYSTEM, content=content)

    def add_user_message(self, content: str) -> "Message":
        return Message.create(chat=self, role=ROLE_USER, content=content)

    def add_assistant_message(self, content: str) -> "Message":
        return Message.create(chat=self, role=ROLE_ASSISTANT, content=content)

    def add_tool_message(self, content: str) -> "Message":
        return Message.create(chat=self, role=ROLE_TOOL, content=content)

    def collect_messages(self) -> List[dict]:
        messages = []
        query = (
            Message.select().where(Message.chat == self).order_by(Message.number.asc())
        )

        for msg in query:
            messages.append({"role": msg.role, "content": msg.content})

        return messages


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
