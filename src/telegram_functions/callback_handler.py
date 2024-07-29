from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.utils.gspread_utils import find_cell_to_update, get_cell_contents
from src.utils.load_config import load_config
from src.utils.utils import get_next_saturday_date, extract_names_coming, extract_names_not_coming

config = load_config('conf/base/config.yaml')

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('weekly_poll_answer_'):
        poll_message_ids = context.bot_data.get('weekly_poll_message_id', {})

        if poll_message_ids and query.message.message_id in poll_message_ids.values():
            user = query.from_user
            user_name = user.first_name
            telehandle = user.username
            current_text = query.message.text
            coming_list = extract_names_coming(current_text)
            not_coming_list = extract_names_not_coming(current_text)
            
            # Update lists based on user's choice
            name_on_poll = f'{user_name} ({telehandle})'
            if query.data == 'weekly_poll_answer_coming':
                if name_on_poll in coming_list:
                    coming_list.remove(name_on_poll)
                else:
                    coming_list.append(name_on_poll)
            elif query.data == 'weekly_poll_answer_not_coming':
                if name_on_poll in not_coming_list:
                    not_coming_list.remove(name_on_poll)
                else:
                    not_coming_list.append(name_on_poll)
            
            # Create updated message text
            new_text = f"""Volunteering Session
📍Geylang Bahru Blk 61&62
🗓️{get_next_saturday_date()} (Sat), 10:30am to 12pm

Pls indicate yr availability by 6pm tmrw(Fri)! Thank you 🧑‍🤝‍🧑
            """
            new_text += "\n\n"
            new_text += f"Coming 🧓 ({len(coming_list)}👥)" + "\n" + "\n".join(coming_list)
            new_text += "\n\n"
            new_text += f"Not Coming 🥲 ({len(not_coming_list)}👥)" + "\n" + "\n".join(not_coming_list)
            
            # Update the message
            keyboard = [
                [InlineKeyboardButton("I'm Coming", callback_data='weekly_poll_answer_coming')],
                [InlineKeyboardButton("Not Free", callback_data='weekly_poll_answer_not_coming')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot_data['weekly_poll_message'] = new_text
            for chat_id, message_id in poll_message_ids.items():
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=new_text,
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    print(f"Failed to update message in chat {chat_id}: {e}")
            
            return

    elif query.data.startswith('override_befriending_senior_'):
        await query.edit_message_reply_markup(reply_markup=None)
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
        await query.edit_message_reply_markup(reply_markup=None)
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
        await query.edit_message_reply_markup(reply_markup=None)
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
            response = f"You selected {befriending_senior_name}. Please enter the updates below. \nExample of update: Mr Wong was always happy to see us and today was no exception. During the session, he shared with us about his childhood stories and experiences in Malaysia. We also found out that one of the light in his apartment was not working and he was having trouble finding a replacement."
            await query.message.reply_text(response)
            context.user_data['MODE_IS_UPDATE_BEFRIENDING_SENIORS'] = True

    elif query.data.startswith('update_frail_senior_'):
        await query.edit_message_reply_markup(reply_markup=None)
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