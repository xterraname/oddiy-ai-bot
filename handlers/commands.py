from telegram import Update
from telegram.ext import ContextTypes
from database.models import User
from utils.middlewares import with_user


@with_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = context.user_db

    msg = (
        f"Salom, {user.first_name}! Botga xush kelibsiz. Menga biror savolingiz bormi? (matn yoki ovozli habar shaklida jo'nating!)"
    )

    await update.message.reply_text(msg)


@with_user
async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = context.user_db
    
    if user.number_chats_left < 1:
        await update.effective_chat.send_message("Chat bo'yicha limitingiz tugagan!")
        return

    chat = user.get_active_chat()
    chat.inactive()

    await update.effective_chat.send_message("Yangi chat yaratildi.")
    await update.effective_chat.send_message("Menga biror savolingiz bormi?")
