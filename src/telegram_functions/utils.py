from telegram import Update
from telegram.ext import ContextTypes

def set_default_user_data(context):
    context.user_data['name_of_befriending_senior_to_be_updated'] = None
    context.user_data['name_of_frail_senior_to_be_updated'] = None
    context.user_data['MODE_IS_UPDATE_BEFRIENDING_SENIORS'] = False
    context.user_data['MODE_IS_UPDATE_FRAIL_SENIORS'] = False

def reset_user_data(context):
    context.user_data.clear()

def start_conversation(update: Update, context):
    # Start the conversation
    context.job_queue.run_once(reset_user_data, 3600)