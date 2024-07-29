from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from src.utils.load_config import load_config
from src.telegram_functions.commands import start_command, help_command, update_befriending_seniors_message_command, update_frail_seniors_message_command, generate_report_command, send_allocations_command
from src.telegram_functions.utils import start_conversation
from src.telegram_functions.update_befriending import update_befriending_senior_message_response_handler
from src.telegram_functions.update_frail import update_frail_senior_message_response_handler
from src.telegram_functions.commands_list.send_allocations import send_allocations_message_response_handler
from src.telegram_functions.callback_handler import handle_button
from src.telegram_functions.scheduler import create_scheduler
from src.utils.utils import is_update_window_closed

from conf.base.creds import TOKEN

config = load_config('conf/base/config.yaml')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Inform if it is group or private chat
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message
    telehandle: str = update.message.from_user.username #tele handle

    # UserID, group/private chat/ incoming message
    print(f'User ({update.message.chat.id}) in {message_type}, {telehandle}: {text}')

    start_conversation(update, context)
    context.user_data.setdefault('name_of_befriending_senior_to_be_updated', None)
    context.user_data.setdefault('name_of_frail_senior_to_be_updated', None)
    context.user_data.setdefault('MODE_IS_UPDATE_BEFRIENDING_SENIORS', False)
    context.user_data.setdefault('MODE_IS_UPDATE_FRAIL_SENIORS', False)
    context.user_data.setdefault('MODE_IS_SEND_ALLOCATIONS', False)

    if update.message.chat.type in ["group", "supergroup"]:
        return

    if context.user_data['MODE_IS_UPDATE_BEFRIENDING_SENIORS']:

        if is_update_window_closed():
            response = "Window for updating of seniors' status this week is closed. Please kindly approach our VM heads Nicholas and Rachel for assistance."
        else:
            response = update_befriending_senior_message_response_handler(update, context)
        
    elif context.user_data['MODE_IS_UPDATE_FRAIL_SENIORS']:
        if is_update_window_closed():
            response = "Window for updating of seniors' status this week is closed. Please kindly approach our VM heads Nicholas and Rachel for assistance."
        else:
            response = update_frail_senior_message_response_handler(update, context)

    elif context.user_data['MODE_IS_SEND_ALLOCATIONS']:
        response = await send_allocations_message_response_handler(update, context)

    else:
        response = "Sorry, request failed!"

    print('Bot:', response)  # For debugging

    await update.message.reply_text(response)

async def handle_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Inform if it is group or private chat
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message
    telehandle: str = update.message.from_user.username #tele handle

    if context.user_data['MODE_IS_SEND_ALLOCATIONS']:
        response = await send_allocations_message_response_handler(update, context)
    else:
        response = "Sorry, request failed!"

    print('Bot:', response)  # For debugging

    await update.message.reply_text(response)

# Logging errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('update_befr_seniors_message',update_befriending_seniors_message_command))
    app.add_handler(CommandHandler('update_frail_seniors_message',update_frail_seniors_message_command))
    app.add_handler(CommandHandler('generate_report', generate_report_command))
    app.add_handler(CommandHandler('send_allocations', send_allocations_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photos))
    # Errors
    app.add_error_handler(error)

    # Scheduler to schedule messages
    create_scheduler(app)

    # Polls the bot
    print('Starting T.H.E.S Bot')
    app.run_polling(poll_interval=3)  # Checks every x seconds for messages
