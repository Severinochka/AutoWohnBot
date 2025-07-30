import psycopg2
from config import DB_CONFIG  # где DB_CONFIG хранит параметры подключения
from config import TOKEN
from translations import translations, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

import json
import logging
import os
import asyncio
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup, WebAppInfo,
    LabeledPrice, PreCheckoutQuery, SuccessfulPayment, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters.command import CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
from zoneinfo import ZoneInfo

# === Configuration ===
WEBAPP_URLS = {
    "en": "https://va3elina.github.io/WebApp/filtersEN.html",
    "de": "https://va3elina.github.io/WebApp/filtersDE.html",
    "ru": "https://va3elina.github.io/WebApp/filtersRU.html",
    "ar": "https://va3elina.github.io/WebApp/filtersAR.html",
    "tr": "https://va3elina.github.io/WebApp/filtersTU.html"
}

PRODUCT_SLUG = "pro_month"
BOT_USERNAME = "AutoWohnBot"
HELP_USERNAME = "@WohnungsBotInfo"

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Bot Initialization ===
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === Create users table ===
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY,
                       first_name
                       TEXT,
                       last_name
                       TEXT,
                       username
                       TEXT,
                       language
                       TEXT
                       DEFAULT
                       'en',
                       location
                       TEXT,
                       min_price
                       INTEGER
                       DEFAULT
                       NULL,
                       max_price
                       INTEGER
                       DEFAULT
                       NULL,
                       min_size
                       INTEGER
                       DEFAULT
                       NULL,
                       max_size
                       INTEGER
                       DEFAULT
                       NULL,
                       tauschwohnung
                       BOOLEAN
                       DEFAULT
                       0,
                       wbs
                       BOOLEAN
                       DEFAULT
                       0,
                       use_immoscout
                       BOOLEAN
                       DEFAULT
                       1,
                       use_kleinanzeigen
                       BOOLEAN
                       DEFAULT
                       1,
                       use_immowelt
                       BOOLEAN
                       DEFAULT
                       1,
                       subscribed_until
                       TEXT,
                       is_searching
                       BOOLEAN
                       DEFAULT
                       0,
                       referred_by
                       INTEGER
                       DEFAULT
                       NULL,
                       use_inberlinwohnen BOOLEAN DEFAULT 1
                   )
                   """)

    # Добавляем недостающие поля, если БД уже создана
    for column, col_type in [
        ("first_name", "TEXT"),
        ("last_name", "TEXT"),
        ("username", "TEXT"),
        ("language", "TEXT DEFAULT 'en'"),
        ("referred_by", "INTEGER DEFAULT NULL")
    ]:
        cursor.execute("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name='users' AND column_name=%s
            """, (column,))
        if not cursor.fetchone():
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {col_type}")
            logger.info(f"[DB] Added column '{column}' of type '{col_type}' to users table.")
    conn.commit()
    conn.close()


# === Language management ===
def get_user_language(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def set_user_language(user_id, lang):
    if lang not in SUPPORTED_LANGUAGES:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = %s WHERE id = %s", (lang, user_id))
    conn.commit()
    conn.close()


def get_language_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="🇬🇧 English"),
            KeyboardButton(text="🇩🇪 Deutsch"),
            KeyboardButton(text="🇷🇺 Русский"),
            KeyboardButton(text="🇦🇪 العربية"),  # Arabic
            KeyboardButton(text="🇹🇷 Türkçe")  # Turkish
        ]
    ], resize_keyboard=True)


def get_main_menu(lang):
    labels = translations[lang]["menu"]
    change_lang = translations[lang]["change_language"]
    help_btn = translations[lang]["help_button"]
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=labels[0]), KeyboardButton(text=labels[1])],
        [KeyboardButton(text=labels[2]), KeyboardButton(text=labels[3])],
        [KeyboardButton(text=labels[4]), KeyboardButton(text=labels[5])],
        [KeyboardButton(text=change_lang), KeyboardButton(text=help_btn)]
    ], resize_keyboard=True)


# === Sanitize surrogate pairs ===
def sanitize(text):
    if not text:
        return None
    return text.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')


# === Add user if not exists ===
async def add_user_to_db(user: types.User, referrer_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = %s", (user.id,))
    if cursor.fetchone() is None:
        trial_end = datetime.now() + timedelta(days=7)

        cursor.execute("""
                       INSERT INTO users (id, first_name, last_name, username, subscribed_until, is_searching,
                                          referred_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       """, (
                           user.id,
                           sanitize(user.first_name),
                           sanitize(user.last_name),
                           user.username,
                           trial_end.isoformat(),
                           0,
                           referrer_id
                       ))
        logger.info(f"[DB] New user added: {user.id} (referred_by={referrer_id})")

        # Бонус пригласившему
        if referrer_id and referrer_id != user.id:  # Защита от самоприглашения
            cursor.execute("SELECT subscribed_until, language FROM users WHERE id = %s", (referrer_id,))
            ref_row = cursor.fetchone()
            if ref_row:
                try:
                    current_sub = datetime.fromisoformat(ref_row[0]) if ref_row[0] else datetime.now()
                except Exception:
                    current_sub = datetime.now()

                bonus_sub = current_sub + timedelta(days=14)
                cursor.execute("UPDATE users SET subscribed_until = %s WHERE id = %s",
                               (bonus_sub.isoformat(), referrer_id))
                logger.info(f"[REFERRAL] User {referrer_id} got +14 days for inviting {user.id}")

                # Notification to referrer
                ref_lang = ref_row[1] if ref_row[1] in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
                try:
                    await bot.send_message(
                        chat_id=referrer_id,
                        text=translations[ref_lang]["referral"]["success"].format(
                            days=14,
                            new_user=user.first_name or "New user"
                        ),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.error(f"[REFERRAL] Error sending notification to {referrer_id}: {e}")
            else:
                logger.warning(f"[REFERRAL] Referrer {referrer_id} not found.")
        else:
            # Existing user - update name/username
            cursor.execute("""
                        UPDATE users SET first_name = %s, last_name = %s, username = %s WHERE id = %s
                    """, (
                sanitize(user.first_name),
                sanitize(user.last_name),
                user.username,
                user.id
            ))
            logger.info(f"[DB] Existing user {user.id} info updated.")

    conn.commit()
    conn.close()


# === Save user filters ===
def save_user_filters(user_id, location, min_price, max_price, min_size, max_size,
                      tauschwohnung=False, wbs=False,
                      use_immoscout=True, use_kleinanzeigen=True, use_immowelt=True, use_inberlinwohnen=True):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO users (id, location, min_price, max_price, min_size, max_size,
                                          tauschwohnung, wbs,
                                          use_immoscout, use_kleinanzeigen, use_immowelt, use_inberlinwohnen)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT(id) DO
                       UPDATE SET
                           location = excluded.location,
                           min_price = excluded.min_price,
                           max_price = excluded.max_price,
                           min_size = excluded.min_size,
                           max_size = excluded.max_size,
                           tauschwohnung = excluded.tauschwohnung,
                           wbs = excluded.wbs,
                           use_immoscout = excluded.use_immoscout,
                           use_kleinanzeigen = excluded.use_kleinanzeigen,
                           use_immowelt = excluded.use_immowelt,
                           use_inberlinwohnen = excluded.use_inberlinwohnen
                       """, (user_id, location, min_price, max_price, min_size, max_size,
                             tauschwohnung, wbs, use_immoscout, use_kleinanzeigen, use_immowelt, use_inberlinwohnen))
        conn.commit()
        conn.close()
        logger.info(f"[DB] User {user_id} filters updated")
    except psycopg2.Error as e:
        logger.error(f"[DB] Error saving filters: {e}")

MENU_ACTIONS = {
    # 🔹 English
    "🔎 Enable Search": "start_search",
    "⛔ Stop Search": "stop_search",
    "🏠 Set Filters": "set_filters",
    "💳 Subscribe": "subscribe",
    "ℹ️ My Subscription": "my_subscription",
    "👥 Invite Friends": "invite",
    "🔙 Back to Menu": "back_to_menu",
    "🌐 Change Language": "change_language",
    "🆘 Help": "help",

    # 🔹 Deutsch
    "🔎 Suche starten": "start_search",
    "⛔ Suche stoppen": "stop_search",
    "🏠 Filter setzen": "set_filters",
    "💳 Abonnieren": "subscribe",
    "ℹ️ Mein Abo": "my_subscription",
    "👥 Freunde einladen": "invite",
    "🔙 Zurück zum Menü": "back_to_menu",
    "🌐 Sprache ändern": "change_language",
    "🆘 Hilfe": "help",

    # 🔹 Русский
    "🔎 Включить поиск": "start_search",
    "⛔ Остановить поиск": "stop_search",
    "🏠 Установить фильтры": "set_filters",
    "💳 Подписка": "subscribe",
    "ℹ️ Моя подписка": "my_subscription",
    "👥 Пригласить друга": "invite",
    "🔙 Назад в меню": "back_to_menu",
    "🌐 Сменить язык": "change_language",
    "🆘 Помощь": "help",

    # Arabic
    "🔎 تمكين البحث": "start_search",
    "⛔ إيقاف البحث": "stop_search",
    "🏠 إعداد الفلاتر": "set_filters",
    "💳 الاشتراك": "subscribe",
    "ℹ️ اشتراكي": "my_subscription",
    "👥 دعوة الأصدقاء": "invite",
    "🔙 العودة إلى القائمة": "back_to_menu",
    "🌐 تغيير اللغة": "change_language",
    "🆘 مساعدة": "help",

    # Turkish
    "🔎 Aramayı Etkinleştir": "start_search",
    "⛔ Aramayı Durdur": "stop_search",
    "🏠 Filtreleri Ayarla": "set_filters",
    "💳 Abone Ol": "subscribe",
    "ℹ️ Aboneliğim": "my_subscription",
    "👥 Arkadaş Davet Et": "invite",
    "🔙 Menüye Dön": "back_to_menu",
    "🌐 Dili Değiştir": "change_language",
    "🆘 Yardım": "help"
}


@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    referrer_id = None
    if command.args:
        try:
            referrer_id = int(command.args)
            if referrer_id == message.from_user.id:
                lang = get_user_language(message.from_user.id)
                await message.answer(translations[lang]["referral"]["self_invite"])
                referrer_id = None
        except ValueError:
            pass

    await add_user_to_db(message.from_user, referrer_id)

    # Уведомление новому пользователю
    if referrer_id:
        lang = get_user_language(message.from_user.id)
        await message.answer(
            translations[lang]["referral"]["new_user_notification"],
            parse_mode="Markdown"
        )

    await message.answer(
        "Please select your language / Bitte wählen Sie Ihre Sprache / Пожалуйста, выберите язык / الرجاء اختيار اللغة / Lütfen dilinizi seçin:",
        reply_markup=get_language_keyboard()
    )


# Обработчик кнопки приглашения друзей
@dp.message(F.text.in_(["👥 Пригласить друга", "👥 Invite Friends", "👥 Freunde einladen", "👥 دعوة الأصدقاء", "👥 Arkadaş Davet Et"]))
async def referral_link_handler(message: types.Message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await message.answer(
        translations[lang]["invite_friends_text"] + f"\n\n🔗 {ref_link}"
    )

@dp.message(F.text.in_(["🆘 Help", "🆘 Hilfe", "🆘 Помощь", "🆘 مساعدة", "🆘 Yardım"]))
async def help_handler(message: types.Message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    await message.answer(
        translations[lang]["help_text"].format(help_username=HELP_USERNAME),
        parse_mode="Markdown"
    )

@dp.message(F.text.in_(["🇬🇧 English", "🇩🇪 Deutsch", "🇷🇺 Русский", "🇦🇪 العربية", "🇹🇷 Türkçe"]))
async def select_language(message: types.Message):
    user_id = message.chat.id
    lang_map = {
        "🇬🇧 English": "en",
        "🇩🇪 Deutsch": "de",
        "🇷🇺 Русский": "ru",
        "🇦🇪 العربية": "ar",
        "🇹🇷 Türkçe": "tr"
    }
    lang = lang_map.get(message.text, DEFAULT_LANGUAGE)
    set_user_language(user_id, lang)
    await add_user_to_db(message.from_user)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subscribed_until FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()

    trial_end_text = ""
    if row and row[0]:
        try:
            sub_until = datetime.fromisoformat(row[0])
            days = (sub_until.date() - datetime.now().date()).days
            trial_end_text = translations[lang]["welcome_message"].format(
                date=sub_until.strftime("%d.%m.%Y"),
                days=days
            )
        except Exception as e:
            logger.warning(f"[START] Error parsing subscription date: {e}")

    await message.answer(
        trial_end_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu(lang)
    )



async def subscribe_handler(message: types.Message):
    lang = get_user_language(message.chat.id)
    prices = [LabeledPrice(label="XTR", amount=250)]

    await message.answer_invoice(
        title=translations[lang]["invoice"]["title"],
        description=translations[lang]["invoice"]["description"],
        payload="subscription_30_days",
        provider_token="",  # Оставь пустым для Telegram Stars
        currency="XTR",
        prices=prices,
        start_parameter="pro_month"
    )


@dp.message(F.text.in_([
    "🌐 Change Language",
    "🌐 Sprache ändern",
    "🌐 Сменить язык",
    "🌐 تغيير اللغة",
    "🌐 Dili Değiştir"
]))
async def change_language(message: types.Message):
    await message.answer(
        "Please select your language / Bitte wählen Sie Ihre Sprache / Пожалуйста, выберите язык / الرجاء اختيار اللغة / Lütfen dilinizi seçin:",
        reply_markup=get_language_keyboard()
    )


@dp.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


# === Check subscription status ===
def check_subscription(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subscribed_until, is_searching FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return False

    try:
        sub_until = datetime.fromisoformat(row[0])
        now = datetime.now()
        if sub_until < now:
            # Subscription expired, disable searching
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_searching = 0 WHERE id = %s", (user_id,))
            conn.commit()
            conn.close()
            return False
        return True
    except Exception as e:
        logger.error(f"[DB] Error checking subscription: {e}")
        return False


def get_subscription_warning_message(subscribed_until: datetime, lang: str) -> str:
    now = datetime.now()
    days_left = (subscribed_until.date() - now.date()).days

    if days_left == 1:
        return translations[lang]["subscription"]["will_expire_tomorrow"]
    elif days_left < 0:
        return translations[lang]["subscription"]["expired_notice"]
    return ""


async def my_subscription_handler(message: types.Message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subscribed_until FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        try:
            sub_until = datetime.fromisoformat(row[0])
            if sub_until > datetime.now():
                remaining = (sub_until - datetime.now()).days
                warning_msg = get_subscription_warning_message(sub_until, lang)
                await message.answer(
                    translations[lang]["subscription"]["active"].format(
                        date=sub_until.date(),
                        days=remaining
                    ) + (f"\n\n{warning_msg}" if warning_msg else ""),
                    parse_mode="Markdown"
                )
            else:
                await message.answer(
                    translations[lang]["subscription"]["expired"],
                    parse_mode="Markdown"
                )
        except Exception as e:
            await message.answer("⚠️ Error checking subscription.")
            logger.warning(f"[Subscription] Date parsing error: {e}")
    else:
        await message.answer(
            translations[lang]["subscription"]["none"],
            parse_mode="Markdown"
        )


@dp.message(F.successful_payment)
async def handle_successful_payment(message: types.Message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    now = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subscribed_until FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()

    if row and row[0]:
        try:
            current_until = datetime.fromisoformat(row[0])
            if current_until > now:
                new_until = current_until + timedelta(days=30)
            else:
                new_until = now + timedelta(days=30)
        except Exception as e:
            logger.warning(f"[PAYMENT] Date parsing error: {e}")
            new_until = now + timedelta(days=30)
    else:
        new_until = now + timedelta(days=30)

    cursor.execute("UPDATE users SET subscribed_until = %s WHERE id = %s", (new_until.isoformat(), user_id))
    conn.commit()
    conn.close()

    await message.answer(
        translations[lang]["subscription"]["activated"].format(
            date=new_until.strftime('%d.%m.%Y')
        ),
        parse_mode="Markdown"
    )


async def open_filters(message: types.Message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    await add_user_to_db(message.from_user)
    # Получаем правильный URL для языка, по умолчанию — немецкий
    webapp_url = WEBAPP_URLS.get(lang, WEBAPP_URLS["de"])

    open_button = KeyboardButton(
        text=translations[lang]["open_webapp"],
        web_app=WebAppInfo(url=webapp_url)
    )

    back_button = KeyboardButton(text=translations[lang]["back_to_menu"])
    markup = ReplyKeyboardMarkup(keyboard=[[open_button], [back_button]], resize_keyboard=True)

    await message.answer(translations[lang]["filters"]["open"], reply_markup=markup)



@dp.message(F.content_type == types.ContentType.WEB_APP_DATA)
async def webapp_data_handler(message: types.Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)

    # Check subscription first
    if not check_subscription(user_id):
        await message.answer(
            translations[lang]["subscription"]["expired"],
            parse_mode="Markdown"
        )
        return

    if not message.web_app_data or not message.web_app_data.data:
        await message.answer(translations[lang]["webapp_error"])
        return

    try:
        data = json.loads(message.web_app_data.data)
        logger.info(f"[WEBAPP] Data received from {message.from_user.id}: {data}")
    except json.JSONDecodeError:
        await message.answer(translations[lang]["webapp_error"])
        return

    price = data.get("price") or [None, None]
    size = data.get("size") or [None, None]
    tauschwohnung = data.get("tauschwohnung", False)
    wbs = data.get("wbs", False)
    websites = data.get("websites", [])

    use_immoscout = "immobilienscout24" in websites
    use_kleinanzeigen = "kleinanzeigen" in websites
    use_immowelt = "immowelt" in websites
    use_inberlinwohnen = "inberlinwohnen" in websites

    location_text = None
    if "location" in data:
        loc = data["location"]
        if loc["type"] == "circle":
            location_text = f"{loc['center'][0]}, {loc['center'][1]}, {loc['radius']}"
        elif loc["type"] == "polygon":
            location_text = "; ".join([f"{p[0]}, {p[1]}" for p in loc["coordinates"]])

    try:
        min_price = int(float(price[0])) if price and len(price) > 0 and price[0] else None
        max_price = int(float(price[1])) if price and len(price) > 1 and price[1] else None
        min_size = int(float(size[0])) if size and len(size) > 0 and size[0] else None
        max_size = int(float(size[1])) if size and len(size) > 1 and size[1] else None
    except (ValueError, TypeError):
        await message.answer(translations[lang]["data_error"])
        return

    save_user_filters(
        user_id=user_id,
        location=location_text,
        min_price=min_price,
        max_price=max_price,
        min_size=min_size,
        max_size=max_size,
        tauschwohnung=tauschwohnung,
        wbs=wbs,
        use_immoscout=use_immoscout,
        use_kleinanzeigen=use_kleinanzeigen,
        use_immowelt=use_immowelt,
        use_inberlinwohnen=use_inberlinwohnen
    )

    # Enable is_searching after filters set
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_searching = 1 WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    logger.info(f"[DB] Search enabled after setting filters for user {user_id}")

    tauschwohnung_text = translations[lang]["filters"]["yes"] if tauschwohnung else translations[lang]["filters"]["no"]
    wbs_text = translations[lang]["filters"]["yes"] if wbs else translations[lang]["filters"]["no"]
    min_price_text = min_price if min_price else translations[lang]["filters"]["not_set"]
    max_price_text = max_price if max_price else translations[lang]["filters"]["not_set"]
    min_size_text = min_size if min_size else translations[lang]["filters"]["not_set"]
    max_size_text = max_size if max_size else translations[lang]["filters"]["not_set"]

    websites_list = []
    if use_immoscout:
        websites_list.append("Scout")
    if use_kleinanzeigen:
        websites_list.append("Kleinanzeigen")
    if use_immowelt:
        websites_list.append("Immowelt")
    if use_inberlinwohnen:
        websites_list.append("InBerlinWohnen")
    websites_text = "/".join(websites_list) if websites_list else translations[lang]["filters"]["not_set"]

    await message.answer(
        translations[lang]["filters"]["saved"].format(
            min_price=min_price_text,
            max_price=max_price_text,
            min_size=min_size_text,
            max_size=max_size_text,
            tauschwohnung=tauschwohnung_text,
            wbs=wbs_text,
            websites=websites_text
        ),
        parse_mode="Markdown",
        reply_markup=get_main_menu(lang)
    )



@dp.message(F.text.in_(MENU_ACTIONS.keys()))
async def handle_menu_actions(message: types.Message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    text = message.text.strip()
    action = MENU_ACTIONS.get(text)

    # Проверка подписки для всех действий, кроме подписки и просмотра подписки
    if action not in ["subscribe", "my_subscription"]:
        if not check_subscription(user_id):
            await message.answer(
                translations[lang]["subscription"]["expired"],
                parse_mode="Markdown"
            )
            return

    if action == "start_search":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT location, use_immoscout, use_kleinanzeigen, use_immowelt, use_inberlinwohnen
            FROM users WHERE id = %s
        """, (user_id,))
        row = cursor.fetchone()
        if not row:
            await message.answer("⚠️ User not found in database.")
            return

        location, scout, klein, welt, inberlin = row
        if not location or not (scout or klein or welt or inberlin):
            await message.answer(
                f"⚠️ {translations[lang]['webapp_error']}\n\n"
                f"{translations[lang]['filters']['open']}",
                reply_markup=get_main_menu(lang)
            )
            return

        cursor.execute("UPDATE users SET is_searching = 1 WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"[DB] User {user_id} started search.")
        await message.answer(translations[lang]["search"]["started"])

    elif action == "stop_search":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_searching = 0 WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"[DB] User {user_id} stopped search.")
        await message.answer(translations[lang]["search"]["stopped"])

    elif action == "set_filters":
        await open_filters(message)

    elif action == "subscribe":
        await subscribe_handler(message)

    elif action == "my_subscription":
        await my_subscription_handler(message)

    elif action == "invite":
        await referral_link_handler(message)



    elif action == "back_to_menu":

        await message.answer(

            translations[lang]["start"],

            reply_markup=get_main_menu(lang)

        )


async def subscription_reminder_loop():
    tz = ZoneInfo("Europe/Berlin")  # Часовой пояс Берлина

    def next_run_times():
        now = datetime.now(tz)
        today_8 = now.replace(hour=8, minute=0, second=0, microsecond=0)
        today_16 = now.replace(hour=16, minute=0, second=0, microsecond=0)

        if now < today_8:
            return today_8
        elif now < today_16:
            return today_16
        else:
            return (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)

    while True:
        try:
            now = datetime.now()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, subscribed_until, language FROM users")
            users = cursor.fetchall()
            conn.close()

            for user_id, sub_until_str, lang in users:
                if not sub_until_str:
                    continue
                try:
                    sub_until = datetime.fromisoformat(sub_until_str)
                except Exception:
                    continue

                days_left = (sub_until.date() - now.date()).days

                if days_left in [3, 2, 1, 0, -1]:
                    if lang not in SUPPORTED_LANGUAGES:
                        lang = DEFAULT_LANGUAGE

                    warning_text = get_subscription_warning_message(sub_until, lang)
                    if warning_text:
                        try:
                            buttons = ReplyKeyboardMarkup(
                                keyboard=[[
                                    KeyboardButton(text=translations[lang]["menu"][3]),  # 💳 Подписка
                                    KeyboardButton(text=translations[lang]["menu"][5])  # 👥 Пригласить друга
                                ]],
                                resize_keyboard=True
                            )
                            await bot.send_message(user_id, warning_text, reply_markup=buttons)
                            logger.info(f"[REMINDER] Sent to {user_id}: {warning_text}")

                        except Exception as e:
                            logger.warning(f"[REMINDER] Failed to notify {user_id}: {e}")

        except Exception as e:
            logger.error(f"[REMINDER_LOOP] Error: {e}")

        # Ждём до следующего запуска (08:00 или 16:00 по Берлину)
        now = datetime.now(tz)
        next_run = next_run_times()
        wait_seconds = (next_run - now).total_seconds()
        logger.info(f"[REMINDER_LOOP] Sleeping for {int(wait_seconds)} seconds until {next_run}")
        await asyncio.sleep(wait_seconds)


# === Entry point ===
async def main():
    create_users_table()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Bot started.")

    # 🔁 Запускаем цикл уведомлений о подписке
    asyncio.create_task(subscription_reminder_loop())

    # ▶️ Запускаем Telegram бота
    await dp.start_polling(bot)

@dp.message()
async def fallback_handler(message: types.Message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    menu_items = translations[lang]["menu"] + [
        translations[lang]["change_language"],
        translations[lang]["back_to_menu"]
    ]

    if message.text in menu_items:
        return  # уже должен был обработаться другим хендлером

    if message.text.startswith("/"):
        return  # Игнорируем команды, типа /start

    user_id = message.chat.id

    # Проверим, есть ли пользователь в БД
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    user_exists = cursor.fetchone()
    conn.close()

    if not user_exists:
        await add_user_to_db(message.from_user)

    # Отправим выбор языка
    await message.answer(
        "Please select your language / Bitte wählen Sie Ihre Sprache / Пожалуйста, выберите язык / الرجاء اختيار اللغة / Lütfen dilinizi seçin:",
        reply_markup=get_language_keyboard()
    )

if __name__ == "__main__":
    asyncio.run(main())