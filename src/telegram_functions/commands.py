# Commands
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from conf.base.creds import BOT_USERNAME, APPROVED_UPLOADER_TELEHANDLES
from src.utils.gspread_utils import get_befriending_seniors_list, get_frail_seniors_list
from src.utils.load_config import load_config
from src.utils.utils import is_update_window_closed
from src.telegram_functions.scheduler import send_report_to_vm_group_message

config = load_config('conf/base/config.yaml')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in private chats.")
        return
    
    await update.message.reply_text('Hello! Welcome to NUS CSC T.H.E.S Bot. For more\
        information about our project, visit https://linktr.ee/T.H.E.Seniors.\n\nRun /update_befr_seniors_message to update befriending senior status and /update_frail_seniors_message to update frail (doorknocking) senior status!')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        await update.message.reply_text(f'Please run this command only in private chat with me. Start by messaging {BOT_USERNAME}')
        return
    await update.message.reply_text('Help.')

async def send_allocations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        return
    if update.message.from_user.username not in APPROVED_UPLOADER_TELEHANDLES:
        await update.message.reply_text('Sorry, you are not authorized to run this command. Please try again later.')
        return
    context.user_data['MODE_IS_SEND_ALLOCATIONS'] = True
    await update.message.reply_text('What would you like to send?')

async def generate_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        return
    await send_report_to_vm_group_message(context)
    return

async def update_befriending_seniors_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message
    telehandle: str = update.message.from_user.username #tele handle
    if update.message.chat.type in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in private chats.")
        return
    
    if is_update_window_closed():
        response = "Window for updating of seniors' status this week is closed. Please kindly approach our VM heads Nicholas and Rachel for assistance."
        await update.message.reply_text(response)
        return

    befriending_seniors_list = get_befriending_seniors_list()
    if len(befriending_seniors_list) == 0:
        error_message = "Oops! There was an error retrieving seniors list!"
        await update.message.reply_text(error_message)
        return
    
    response = "Which senior's details would you wish to update?"

    keyboard = []
    for name in befriending_seniors_list:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"update_befriending_senior_{name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup)

async def update_frail_seniors_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message
    telehandle: str = update.message.from_user.username #tele handle

    if update.message.chat.type in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in private chats.")
        return
    
    if is_update_window_closed():
        response = "Window for updating of seniors' status this week is closed. Please kindly approach our VM heads Nicholas and Rachel for assistance."
        await update.message.reply_text(response)
        return
    
    frail_seniors_list = sorted(get_frail_seniors_list())
    if len(frail_seniors_list) == 0:
        error_message = "Oops! There was an error retrieving seniors list!"
        await update.message.reply_text(error_message)
        return
    
    response = "Which senior's details would you wish to update?"

    keyboard = []
    for name in frail_seniors_list:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"update_frail_senior_{name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(response, reply_markup=reply_markup)