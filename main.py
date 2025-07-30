import subprocess
import sys
import threading
import time
import requests
import asyncio

from config import ADMIN_ID, BOT_TOKEN

from Immoscout_bd import run as run_immoscout
from Immowelt import run as run_immowelt
from telegram_sender import run as run_sender
from Kleinanzeigen import run as run_kleinanzeigen
from clean_database import run as run_cleanup
from InBerlinwohnen import run as run_inberlinwohnen
from bot_admin import run_admin_bot

TELEGRAM_TOKEN = BOT_TOKEN

def send_error_message(context, error):
    try:
        error_type = type(error).__name__
        error_msg = str(error)
        text = (
            f"🚨 *Ошибка в блоке:* `{context}`\n"
            f"🔴 *Тип:* `{error_type}`\n"
            f"💬 *Описание:* `{error_msg}`"
        )
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_ID, "text": text, "parse_mode": "Markdown"}
        )
    except Exception as e:
        print(f"❌ Не удалось отправить сообщение в Telegram: {e}")

def run_telegram_bot():
    subprocess.run([sys.executable, "telegram.py"])

def run_admin_bot_async():
    asyncio.run(run_admin_bot())  # ✅ Добавлено

if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    print("🤖 Telegram-бот запущен")

    threading.Thread(target=run_admin_bot_async, daemon=True).start()  # ✅ Запуск админ-бота
    print("🛠️ Админ-бот запущен")

    while True:
        print("🔍 Проверка новых объявлений...")

        start_time = time.time()
        found_new = False

        try:
            try:
                if run_immoscout():
                    found_new = True
            except Exception as e:
                send_error_message("Immoscout", e)

            try:
                if run_immowelt():
                    found_new = True
            except Exception as e:
                send_error_message("Immowelt", e)

            try:
                if run_kleinanzeigen():
                    found_new = True
            except Exception as e:
                send_error_message("Kleinanzeigen", e)

            try:
                if run_inberlinwohnen():
                    found_new = True
            except Exception as e:
                send_error_message("InBerlinWohnen", e)

            if found_new:
                print("📬 Новые объявления найдены! Отправляем пользователям...")
                try:
                    run_sender()
                except Exception as e:
                    send_error_message("Рассылка Telegram", e)
            else:
                print("⏳ Новых объявлений нет.")

            try:
                print("🧹 Очистка базы данных после парсинга...")
                run_cleanup()
            except Exception as e:
                send_error_message("Очистка БД", e)

        except Exception as e:
            send_error_message("Main loop", e)

        duration = time.time() - start_time
        if duration > 180:
            try:
                raise TimeoutError(f"Цикл длился слишком долго: {round(duration)} сек")
            except TimeoutError as e:
                send_error_message("Main loop (длительность)", e)

        print("🔁 Ожидание 60 секунд...\n")
        time.sleep(60)
