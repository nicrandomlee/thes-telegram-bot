from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from src.utils.load_config import load_config
from conf.base.creds import chat_id, BOT_USERNAME

config = load_config('conf/base/config.yaml')

async def send_post_volunteering_update_message(context):
    await context.bot.send_message(chat_id=chat_id, text=f"Hi volunteers who attended today's session, could you fill in the updates for today by messaging {BOT_USERNAME} and running the commands /update_befr_seniors_message /update_frail_seniors_message? Thank you and have a good weekend!")

def create_scheduler(app):
    scheduler = AsyncIOScheduler()
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
    )
    scheduler.start()