from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database.db import init_db

# Handlers import
from handlers.commands import start, new_chat
from handlers.chat import chat


def main():
    print("Bot ishga tushmoqda...")

    # DB init
    init_db()

    # Bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newchat", new_chat))
    
    # Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Run bot
    print("Bot ishlayapti...")
    app.run_polling()


if __name__ == "__main__":
    main()
