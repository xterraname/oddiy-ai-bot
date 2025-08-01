import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DB_NAME = os.getenv("DB_NAME", "bot.db")

# Together
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
