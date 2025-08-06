import html
import json
import tempfile
import requests
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database.models import User
from utils.middlewares import with_user
from api.chat import get_answer
from api.connect import get_client
from config import STT_API_URL


def ai_func(telegram_id: int, info_type: str):
    user: User = User.get_or_none(telegram_id=telegram_id)
    if not user:
        return "User not found"

    if info_type == "chat":
        result = {
            "number_chats": user.number_chats,
            "number_chats_left": user.number_chats_left,
        }
        return json.dumps(result)
    elif info_type == "account":
        result = {"telegram_id": telegram_id, "name": user.first_name}
        return json.dumps(result)

    return "Unknown data type."


@with_user
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        await update.message.reply_text("Bot faqat shaxsiy chatda ishlaydi!")
        return

    user: User = context.user_db
    chat = user.get_active_chat()

    if not chat.check_limit_messages():
        await update.effective_chat.send_message(
            "Bitta chatdagi habar soni cheklangan! Iltimos yangi chat oching."
        )
        return

    if update.message.voice:
        voice = update.message.voice
        tg_file = await context.bot.get_file(voice.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg") as temp_file:
            await tg_file.download_to_drive(temp_file.name)

            with open(temp_file.name, "rb") as f:
                response = requests.post(STT_API_URL, files={"file": f})

            if response.status_code == 200:
                result = response.json()
                text = result["transcription"]
                await update.message.reply_text(f"Sizning habaringiz:\n{text}")
            else:
                await update.message.reply_text(
                    f"❌ Ovozni matnga o'girishda xatolik yuzaga keldi"
                )
                temp_file.close()
                return
    else:
        text = update.message.text

    chat.add_user_message(text)

    client = get_client()

    def ask_ai():
        messages = chat.collect_messages()
        return get_answer(client, messages)

    response_text = ask_ai()

    if response_text.startswith("FUNC_CALL:"):
        parts = response_text.split()
        func_name = parts[1]
        param = parts[2] if len(parts) > 2 else None

        if func_name == "get_user_info":
            result = ai_func(user.telegram_id, param)

            chat.add_assistant_message(response_text)
            chat.add_tool_message(result)

            response_text = ask_ai()

    await update.message.reply_text(
        html.escape(response_text), parse_mode=ParseMode.HTML
    )
    chat.add_assistant_message(response_text)
