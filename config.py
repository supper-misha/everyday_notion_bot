import os
from dotenv import load_dotenv
from notion_client import Client
import telebot

load_dotenv()

# Notion настройки
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

if not NOTION_TOKEN:
    raise ValueError("❌ Переменная окружения NOTION_TOKEN не установлена!")

# Telegram настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
ID = os.getenv("ID")

if not BOT_TOKEN:
    raise ValueError("❌ Переменная окружения TELEGRAM_TOKEN не установлена!")

if not ID:
    raise ValueError("❌ Переменная окружения ID не установлена!")

# Инициализация клиентов
notion = Client(auth=NOTION_TOKEN, notion_version="2025-09-03")
bot = telebot.TeleBot(BOT_TOKEN)
