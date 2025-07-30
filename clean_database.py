# -*- coding: utf-8 -*-
import psycopg2
import requests
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
import os
import time
from config import DB_CONFIG, IMMOSCOUT_HEADERS, IMMOSCOUT_CLIENT_ID, IMMOSCOUT_CLIENT_SECRET

BATCH_SIZE = 100
STATE_FILE_NULL = "last_checked_id_null.txt"
STATE_FILE_ACTIVE = "last_checked_id_active.txt"
MODE_STATE_FILE = "mode_state.txt"

CLIENT_ID = "ImmobilienScout24-iPhone-Wohnen-AppKey"
CLIENT_SECRET = "pMxNytaNhHPujeeK"

def get_immoscout_token():
    token_url = "https://publicauth.immobilienscout24.de/oauth/token"
    params = {
        "client_id": CLIENT_ID,
        "grant_type": "client_credentials",
        "client_secret": CLIENT_SECRET
    }
    resp = requests.post(token_url, params=params)
    resp.raise_for_status()
    return resp.json().get("access_token")

def immoscout_is_active(data):
    return data.get("header", {}).get("publicationState", "").lower() == "active"

def check_immoscout_listing(obj_id, headers):
    url = f"https://api.mobile.immobilienscout24.de/expose/{obj_id}?adType=RENT"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return "not_found"
        resp.raise_for_status()
        return "active" if immoscout_is_active(resp.json()) else "inactive"
    except:
        return "error"

def check_immowelt_listing(full_id):
    obj_id = full_id[len("estate_"):] if full_id.startswith("estate_") else full_id
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(f"https://www.immowelt.de/expose/{obj_id}", headers=headers, timeout=10)
        return "active" if resp.status_code == 200 else "not_found" if resp.status_code == 404 else "inactive"
    except:
        return "error"

def check_kleinanzeigen_listing(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        print(f"🌍 [clean_db] Проверка Kleinanzeigen: {url}")
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return "deleted"
        soup = BeautifulSoup(resp.text, "html.parser")
        spans = soup.find_all('span', class_='pvap-reserved-title')
        for span in spans:
            if 'is-hidden' in span.get('class', []) or 'display:none' in span.get('style', '').replace(' ', ''):
                continue
            txt = span.get_text(strip=True).lower()
            if 'reserviert' in txt: return "reserved"
            if 'gelöscht' in txt: return "deleted"
        return "active"
    except:
        return "error"

def read_mode():
    if not os.path.exists(MODE_STATE_FILE): return "null"
    with open(MODE_STATE_FILE, 'r') as f: return f.read().strip()

def save_mode(mode):
    with open(MODE_STATE_FILE, 'w') as f: f.write(mode)

def get_last_checked_id(mode):
    path = STATE_FILE_NULL if mode == "null" else STATE_FILE_ACTIVE
    try:
        if os.path.exists(path):
            with open(path, 'r') as f: return f.read().strip()
    except Exception as e:
        print(f"⚠️ Не удалось прочитать {path}: {e}")
    return None

def save_last_checked_id(last_id, mode):
    path = STATE_FILE_NULL if mode == "null" else STATE_FILE_ACTIVE
    try:
        with open(path, 'w') as f: f.write(str(last_id))
    except Exception as e:
        print(f"⚠️ Не удалось сохранить {path}: {e}")

def get_next_batch(conn, last_id, is_null_mode):
    cursor = conn.cursor()
    condition = "is_active IS NULL" if is_null_mode else "is_active = TRUE"
    if last_id:
        cursor.execute(f"""
            SELECT * FROM listings
            WHERE {condition} AND id > %s
            ORDER BY id
            LIMIT %s
        """, (last_id, BATCH_SIZE))
        batch = cursor.fetchall()
        if not batch:
            cursor.execute(f"""
                SELECT * FROM listings
                WHERE {condition}
                ORDER BY id
                LIMIT %s
            """, (BATCH_SIZE,))
            return cursor.fetchall()
        return batch
    else:
        cursor.execute(f"""
            SELECT * FROM listings
            WHERE {condition}
            ORDER BY id
            LIMIT %s
        """, (BATCH_SIZE,))
        return cursor.fetchall()

def run():
    try:
        MAX_RUNTIME = 100
        start_time = time.time()

        mode = read_mode()
        is_null_mode = mode == "null"
        next_mode = "active" if is_null_mode else "null"

        token = get_immoscout_token()
        headers = {
            "Authorization": f"Bearer {token}",
            **IMMOSCOUT_HEADERS
        }

        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        last_id = get_last_checked_id(mode)
        batch = get_next_batch(conn, last_id, is_null_mode)

        if not batch:
            print("🟡 Нет записей — переключаем режим")
            save_mode(next_mode)
            conn.close()
            return

        for row in batch:
            if time.time() - start_time > MAX_RUNTIME:
                print("⏱️ Время вышло — завершаем итерацию")
                break

            row_dict = dict(zip([desc.name for desc in cursor.description], row))
            checker_type = (
                "kleinanzeigen" if row_dict["source_kleinanzeigen"] else
                "immowelt" if row_dict["source_immowelt"] else
                "immoscout" if row_dict["source_immoscout"] else None
            )
            if not checker_type:
                continue

            if checker_type == "immoscout":
                obj_id = int(row_dict['id']) if row_dict['id'].isdigit() else row_dict['id']
                status = check_immoscout_listing(obj_id, IMMOSCOUT_HEADERS)
            elif checker_type == "immowelt":
                status = check_immowelt_listing(row_dict['id'])
            elif checker_type == "kleinanzeigen":
                status = check_kleinanzeigen_listing(row_dict['url'])
            else:
                status = None

            is_active = status == "active"
            now = datetime.now().isoformat()

            if not is_active:
                cursor.execute("DELETE FROM listings WHERE id = %s", (row_dict['id'],))
            else:
                cursor.execute("""
                    UPDATE listings SET is_active = TRUE, last_checked = %s
                    WHERE id = %s
                """, (now, row_dict['id']))

            last_id = row_dict['id']
            sleep(1)

        save_last_checked_id(last_id, mode)
        save_mode(next_mode)
        conn.close()

    except Exception as e:
        print(f"🔥 Ошибка в процессе очистки: {e}")

if __name__ == "__main__":
    print("🧹 Запуск очистки вручную...")
    run()
