from telegram import Update
from telegram.ext import ContextTypes
from src.utils.gspread_utils import find_cell_to_update, update_cell_with_msg
from src.telegram_functions.utils import set_default_user_data
from src.utils.load_config import load_config

config = load_config('conf/base/config.yaml')

def update_befriending_senior_message_response_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message, expected value is message to be updated
    telehandle: str = update.message.from_user.username #tele handle

    sheet_name = config['google_sheets']['befriending_seniors_update_sheet_name']
    target_senior_name = context.user_data['name_of_befriending_senior_to_be_updated']
    cell_to_update_tuple = find_cell_to_update(target_senior_name, sheet_name=sheet_name)
    update_cell_with_msg(cell_to_update_tuple, text, sheet_name=sheet_name)
    
    # Reset all contexts
    set_default_user_data(context)

    return f"Successfully updated {target_senior_name}'s status. To update another senior's updates, run /update_befr_seniors_message"