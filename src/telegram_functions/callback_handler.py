from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.utils.gspread_utils import find_cell_to_update, get_cell_contents
from src.utils.load_config import load_config

config = load_config('conf/base/config.yaml')

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    if query.data.startswith('override_befriending_senior_'):
        override_status = query.data.split('override_befriending_senior_', 1)[1].lower()
        if override_status == "yes":
            response = f"You selected {context.user_data['name_of_befriending_senior_to_be_updated']}. Please enter the updates below:"
            await query.message.reply_text(response)
            context.user_data['MODE_IS_UPDATE_BEFRIENDING_SENIORS'] = True
        else:
            response = f"Updating of {context.user_data['name_of_befriending_senior_to_be_updated']}'s updates cancelled. Please run /update_befr_seniors_message to update another senior's updates."
            await query.message.reply_text(response)
        return
    
    elif query.data.startswith('override_frail_senior_'):
        override_status = query.data.split('override_frail_senior_', 1)[1].lower()
        if override_status == "yes":
            response = f"You selected {context.user_data['name_of_frail_senior_to_be_updated']}. Please enter the updates below:"
            await query.message.reply_text(response)
            context.user_data['MODE_IS_UPDATE_FRAIL_SENIORS'] = True
        else:
            response = f"Updating of {context.user_data['name_of_frail_senior_to_be_updated']}'s updates cancelled. Please run /update_frail_seniors_message to update another senior's updates."
            await query.message.reply_text(response)
        return
        

    elif query.data.startswith('update_befriending_senior_'):
        sheet_name = config['google_sheets']['befriending_seniors_update_sheet_name']
        befriending_senior_name = query.data.split('update_befriending_senior_', 1)[1]  # Extract the name from callback_data

        context.user_data['name_of_befriending_senior_to_be_updated'] = befriending_senior_name
        cell_to_update_tuple = find_cell_to_update(befriending_senior_name, sheet_name=sheet_name)
        cell_contents = get_cell_contents(cell_to_update_tuple, sheet_name=sheet_name)

        if cell_contents != None:
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='override_befriending_senior_yes')],
                [InlineKeyboardButton("No", callback_data='override_befriending_senior_no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(f"This cell has already been updated with the following updates:\n{cell_contents}\n\nOverride values?", reply_markup=reply_markup)
        else:
            response = f"You selected {befriending_senior_name}. Please enter the updates below:"
            await query.message.reply_text(response)
            context.user_data['MODE_IS_UPDATE_BEFRIENDING_SENIORS'] = True

    elif query.data.startswith('update_frail_senior_'):
        sheet_name = config['google_sheets']['frail_seniors_update_sheet_name']

        frail_senior_name = query.data.split('update_frail_senior_', 1)[1]  # Extract the name from callback_data
        context.user_data['name_of_frail_senior_to_be_updated'] = frail_senior_name
        cell_to_update_tuple = find_cell_to_update(frail_senior_name, sheet_name=sheet_name)
        cell_contents = get_cell_contents(cell_to_update_tuple, sheet_name=sheet_name)

        if cell_contents != None:
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='override_frail_senior_yes')],
                [InlineKeyboardButton("No", callback_data='override_frail_senior_no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(f"This cell has already been updated with the following updates:\n{cell_contents}\n\nOverride values?", reply_markup=reply_markup)
        else:
            response = f"You selected {frail_senior_name}. Please enter the updates below:"
            await query.message.reply_text(response)
            context.user_data['MODE_IS_UPDATE_FRAIL_SENIORS'] = True