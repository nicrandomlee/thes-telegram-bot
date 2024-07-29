from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.utils.load_config import load_config
from src.utils.utils import get_next_saturday_date, extract_names_coming, get_doc_filepath_from_folder, delete_all_files_from_folder
from conf.base.creds import BOT_USERNAME, vm_chat_id, CHAT_IDS
from src.utils.gspread_utils import get_list_of_befriending_seniors_not_updated, get_list_of_frail_seniors_not_updated
from src.utils.docx_utils import generate_report_from_template

config = load_config('conf/base/config.yaml')

async def send_post_volunteering_update_message(context):
    for chat_id in CHAT_IDS:
        await context.bot.send_message(chat_id=chat_id, text=f"Hi volunteers who attended today's session, could you fill in the updates for today by messaging {BOT_USERNAME} and running the commands /update_befr_seniors_message for befriending seniors and /update_frail_seniors_message for doorknocking seniors? Thank you and have a good weekend!")

async def send_post_volunteering_reminder_to_update_status_message(context):
    list_of_befriending_seniors_not_updated = get_list_of_befriending_seniors_not_updated()
    list_of_frail_seniors_not_updated = get_list_of_frail_seniors_not_updated()
    text = f"This is a scheduled report for status on seniors:"
    text += "\n\n"
    text += "These are the befriending seniors whose statuses are not updated:\n" if len(list_of_befriending_seniors_not_updated) > 0 else "All befriending seniors' status have been updated."
    text += '\n'.join(list_of_befriending_seniors_not_updated) if len(list_of_befriending_seniors_not_updated) > 0 else ""
    text += '\n\n'
    text += "These are the frail seniors whose statuses are not updated:\n" if len(list_of_frail_seniors_not_updated) > 0 else "All frail seniors' status have been updated."
    text += '\n'.join(list_of_frail_seniors_not_updated) if len(list_of_frail_seniors_not_updated) > 0 else ""
    text += "\n\nHave a great weekend ahead!"

    for chat_id in CHAT_IDS:
        await context.bot.send_message(chat_id=chat_id, text=text)

async def create_weekly_poll_message(context):
    keyboard = [
                [InlineKeyboardButton("I'm Coming", callback_data='weekly_poll_answer_coming')],
                [InlineKeyboardButton("Not Free", callback_data='weekly_poll_answer_not_coming')]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"""Volunteering Session
📍Geylang Bahru Blk 61&62
🗓️{get_next_saturday_date()}(Sat) , 10:30am to 12pm

Pls indicate yr availability by 6pm tmrw(Fri)! Thank you 🧑‍🤝‍🧑
    """
    
    context.bot_data['weekly_poll_message_id'] = {}
    for chat_id in CHAT_IDS:
        message = await context.bot.send_message(chat_id=chat_id, 
                                    text=text, reply_markup=reply_markup)
        context.bot_data['weekly_poll_message_id'][chat_id] = message.message_id


async def stop_weekly_poll_message(context):

    chat_id = CHAT_IDS[0]
    weekly_poll_message_id = context.bot_data.get('weekly_poll_message_id').get(chat_id)
    if weekly_poll_message_id and chat_id:
        current_text = context.bot_data.get('weekly_poll_message')
        coming_list = extract_names_coming(current_text)
        new_text = f"""Hi all, thanks for polling. This is the final attendance for Volunteering Session
📍Geylang Bahru Blk 61&62
🗓️{get_next_saturday_date()} (Sat), 10:30am to 12pm"""

        new_text += "\n\n"
        new_text += f"Coming 🧓 ({len(coming_list)}👥)" + "\n" + "\n".join(coming_list) if coming_list else "Coming: None"

    for chat_id in CHAT_IDS:
        weekly_poll_message_id = context.bot_data.get('weekly_poll_message_id').get(chat_id)
        if weekly_poll_message_id and chat_id and new_text:
            
            # Send the final attendance message
            await context.bot.send_message(chat_id=chat_id, text=new_text)

            # Delete the original poll message
            await context.bot.delete_message(chat_id=chat_id, message_id=weekly_poll_message_id)

        # Clear the stored message ID and chat ID
    context.bot_data.pop('weekly_poll_message_id', None)
    context.bot_data.pop('weekly_poll_message', None)

async def send_report_to_vm_group_message(context):
    file_path = config['generate_report_from_template_settings']['template_path']
    report_folder = config['generate_report_from_template_settings']['report_folder']
    delete_all_files_from_folder(report_folder)
    generate_report_from_template(file_path)
    report_filepath = get_doc_filepath_from_folder(report_folder)
    with open(report_filepath, 'rb') as document:
        await context.bot.send_message(chat_id=vm_chat_id, text="Hi all, please find below this week's report. This message is automatically generated")
        await context.bot.send_document(chat_id=vm_chat_id, document=document)

    

def create_scheduler(app):
    scheduler = AsyncIOScheduler()
    add_post_volunteering_update_message_job(app, scheduler)
    add_create_weekly_poll_message_job(app, scheduler)
    add_stop_weekly_poll_message_job(app, scheduler)
    add_send_post_volunteering_reminder_to_update_status_message_job(app, scheduler)
    add_send_report_to_vm_group_message_job(app, scheduler)
    add_send_report_to_vm_group_message_2_job(app, scheduler)
    scheduler.start()

def add_post_volunteering_update_message_job(app, scheduler):
    day_of_week = config['post_volunteering_update_message_scheduler']['day_of_week']
    hour = config['post_volunteering_update_message_scheduler']['hour']
    minute = config['post_volunteering_update_message_scheduler']['minute']
    scheduler.add_job(
        send_post_volunteering_update_message,
        trigger=CronTrigger(
            day_of_week=day_of_week, hour=hour, 
            minute=minute, 
            timezone=pytz.timezone('Asia/Singapore')),
        args=[app],
        misfire_grace_time=60
    )

def add_send_post_volunteering_reminder_to_update_status_message_job(app, scheduler):
    day_of_week = config['post_volunteering_reminder_to_update_status_scheduler']['day_of_week']
    hour = config['post_volunteering_reminder_to_update_status_scheduler']['hour']
    minute = config['post_volunteering_reminder_to_update_status_scheduler']['minute']
    scheduler.add_job(
        send_post_volunteering_reminder_to_update_status_message,
        trigger=CronTrigger(
            day_of_week=day_of_week, hour=hour, 
            minute=minute, 
            timezone=pytz.timezone('Asia/Singapore')),
        args=[app],
        misfire_grace_time=60
    )

def add_create_weekly_poll_message_job(app, scheduler):
    day_of_week = config['create_weekly_poll_message_scheduler']['day_of_week']
    hour = config['create_weekly_poll_message_scheduler']['hour']
    minute = config['create_weekly_poll_message_scheduler']['minute']
    scheduler.add_job(
        create_weekly_poll_message,
        trigger=CronTrigger(
            day_of_week=day_of_week, hour=hour, 
            minute=minute, 
            timezone=pytz.timezone('Asia/Singapore')),
        args=[app],
        misfire_grace_time=60
    )

def add_stop_weekly_poll_message_job(app, scheduler):
    day_of_week = config['stop_weekly_poll_message_scheduler']['day_of_week']
    hour = config['stop_weekly_poll_message_scheduler']['hour']
    minute = config['stop_weekly_poll_message_scheduler']['minute']
    scheduler.add_job(
        stop_weekly_poll_message,
        trigger=CronTrigger(
            day_of_week=day_of_week, hour=hour, 
            minute=minute, 
            timezone=pytz.timezone('Asia/Singapore')),
        args=[app],
        misfire_grace_time=60
    )

def add_send_report_to_vm_group_message_job(app, scheduler):
    day_of_week = config['send_report_to_vm_group_scheduler']['day_of_week']
    hour = config['send_report_to_vm_group_scheduler']['hour']
    minute = config['send_report_to_vm_group_scheduler']['minute']
    scheduler.add_job(
        send_report_to_vm_group_message,
        trigger=CronTrigger(
            day_of_week=day_of_week, hour=hour, 
            minute=minute, 
            timezone=pytz.timezone('Asia/Singapore')),
        args=[app],
        misfire_grace_time=60
    )

def add_send_report_to_vm_group_message_2_job(app, scheduler):
    day_of_week = config['send_report_to_vm_group_scheduler_2']['day_of_week']
    hour = config['send_report_to_vm_group_scheduler_2']['hour']
    minute = config['send_report_to_vm_group_scheduler_2']['minute']
    scheduler.add_job(
        send_report_to_vm_group_message,
        trigger=CronTrigger(
            day_of_week=day_of_week, hour=hour, 
            minute=minute, 
            timezone=pytz.timezone('Asia/Singapore')),
        args=[app],
        misfire_grace_time=60
    )