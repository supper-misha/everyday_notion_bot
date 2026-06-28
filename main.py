import config
import routin
import tg_routin
import scheduler
import notion_calendar
from config import bot
from scheduler import start_scheduler

scheduler = start_scheduler()

bot.infinity_polling()
