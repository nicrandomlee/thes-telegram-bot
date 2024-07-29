from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.telegram_functions.utils import set_default_user_data
from src.utils.load_config import load_config
from conf.base.creds import CHAT_IDS

config = load_config('conf/base/config.yaml')

async def send_allocations_message_response_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message, expected value is message to be updated
    telehandle: str = update.message.from_user.username #tele handle
    if text:
        return "Please upload a valid file!"
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        file = file.file_id
        for chat_id in CHAT_IDS:
            caption = "Hi all, please refer to the allocations above for the upcoming volunteering session. See yall soon!"
            await context.bot.send_photo(chat_id=chat_id, photo=file, caption=caption)
    else:
        return "Please upload a valid file!"
    
    # Reset all contexts
    set_default_user_data(context)

    return f"File successfully sent!"
