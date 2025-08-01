from telegram import Update
from telegram.ext import ContextTypes
from database.models import User
from utils.middlewares import with_user


@with_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = context.user_db

    msg = (
        f"Salom, {user.first_name}! Botga xush kelibsiz. Menga biror savolingiz bormi?"
    )

    await update.message.reply_text(msg)
