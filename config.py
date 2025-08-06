import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DB_NAME = os.getenv("DB_NAME", "bot.db")

# Together
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

# STT
STT_API_URL = os.getenv("STT_API_URL", "http://127.0.0.1:8585/transcribe")
