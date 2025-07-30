import psycopg2
import pandas as pd
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import Message, BufferedInputFile
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from config import DB_CONFIG, ADMIN_ID, ADMIN_TOKEN
from datetime import datetime
from zoneinfo import ZoneInfo
from config import DB_CONFIG, ADMIN_ID, ADMIN_TOKEN


BERLIN_TZ = ZoneInfo("Europe/Berlin")

bot = Bot(token=ADMIN_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def export_table_to_excel(table_name: str) -> str:
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    filepath = f"{table_name}.xlsx"
    df.to_excel(filepath, index=False)
    conn.close()
    return filepath

@router.message(Command("start"))
async def start(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "👋 Админ-бот запущен. Доступные команды:\n"
        "/export_users — 📄 выгрузить таблицу users\n"
        "/export_listings — 🏘 выгрузить таблицу listings\n"
        "/set_sub ID YYYY-MM-DD — 🛠 выдать подписку вручную\n"
        "/stats — 📊 показать статистику подписок и поисков"
    )

@router.message(Command("export_users"))
async def export_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    path = export_table_to_excel("users")
    with open(path, "rb") as file:
        content = file.read()
        await message.answer_document(BufferedInputFile(content, filename=path))

@router.message(Command("export_listings"))
async def export_listings(message: Message):
    if not is_admin(message.from_user.id):
        return
    path = export_table_to_excel("listings")
    with open(path, "rb") as file:
        content = file.read()
        await message.answer_document(BufferedInputFile(content, filename=path))

@router.message(Command("set_sub"))
async def set_subscription(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, user_id, date_str = message.text.strip().split()
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET subscribed_until = %s WHERE id = %s", (date_str, user_id))
        conn.commit()
        conn.close()
        await message.answer(f"✅ Подписка пользователю <b>{user_id}</b> установлена до <b>{date_str}</b>")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}\nФормат: /set_sub user_id YYYY-MM-DD")

@router.message(Command("stats"))
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE subscribed_until > CURRENT_TIMESTAMP")
        active_subs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE is_searching = 1")
        searching_users = cursor.fetchone()[0]

        conn.close()

        await message.answer(
            f"📊 <b>Статистика:</b>\n"
            f"👥 Всего пользователей: <b>{total_users}</b>\n"
            f"💳 Активных подписок: <b>{active_subs}</b>\n"
            f"🔍 Активных поисков: <b>{searching_users}</b>"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики: {e}")

async def run_admin_bot():
    await dp.start_polling(bot)
