from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from database.models import User
from utils.middlewares import with_user
from api.chat import get_answer
from api.connect import get_client


@with_user
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        await update.message.reply_text("Bot faqat shaxsiy chatda ishlaydi!")

    text = update.message.text

    user: User = context.user_db

    chat = user.get_active_chat()

    chat.add_user_message(text)

    messages = chat.collect_messages()

    client = get_client()

    response_text = get_answer(client, messages)

    await update.message.reply_text(response_text)

    chat.add_assistant_message(response_text)
