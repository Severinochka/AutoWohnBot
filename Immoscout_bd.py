import psycopg2
import requests
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from config import DB_CONFIG, IMMOSCOUT_CLIENT_ID, IMMOSCOUT_CLIENT_SECRET, IMMOSCOUT_HEADERS

BERLIN_TZ = ZoneInfo("Europe/Berlin")


def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # Создание таблицы listings, если не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            url TEXT,
            price REAL,
            price_warm REAL,
            size REAL,
            address TEXT,
            lat REAL,
            lon REAL,
            swapflat INTEGER,
            wbs_required INTEGER,
            created_at TEXT,
            source_immoscout INTEGER,
            source_kleinanzeigen INTEGER,
            source_immowelt INTEGER,
            photo_url TEXT,
            is_active TEXT,
            last_checked TEXT,
            source_wggesucht INTEGER,
            source_inberlinwohnen INTEGER
        )
    """)
    conn.commit()
    return conn, cursor


def was_seen(cursor, obj_id):
    cursor.execute("SELECT 1 FROM listings WHERE id = %s", (obj_id,))
    return cursor.fetchone() is not None


def mark_as_seen(conn, cursor, obj_id, listing):
    cursor.execute("""
        INSERT INTO listings (
            id, url, price, price_warm, size, address, lat, lon, swapflat,
            wbs_required, created_at, source_immoscout, source_kleinanzeigen,
            source_immowelt, photo_url, is_active, last_checked,
            source_wggesucht, source_inberlinwohnen
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (
        obj_id,
        listing["url"],
        listing["price"],
        listing["price_warm"],
        listing["size"],
        listing["address"],
        listing["lat"],
        listing["lon"],
        int(listing["swapflat"]),
        int(listing["wbs_required"]),
        datetime.now(BERLIN_TZ).isoformat(timespec="seconds"),
        1, 0, 0,  # source_immoscout, source_kleinanzeigen, source_immowelt
        listing["photo_url"],
        "1",
        datetime.now(BERLIN_TZ).isoformat(timespec="seconds"),
        0, 0  # source_wggesucht, source_inberlinwohnen
    ))
    conn.commit()


def clean_price_size(value):
    if not value:
        return None
    val = value.replace("\xa0", "").replace("€", "").replace("m²", "").strip()
    if val.count(",") > 1:
        return None
    if "," in val:
        last_dot = val.rfind(".")
        comma_pos = val.find(",")
        if last_dot != -1 and comma_pos < last_dot:
            return None
    val = val.replace(".", "").replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None


def geocode_address(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "addressdetails": 1, "limit": 1}
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ImmoScoutBot/1.0)"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None, None


def extract_warmmiete(data):
    for section in data.get("sections", []):
        if section.get("type") == "TOP_ATTRIBUTES":
            for attr in section.get("attributes", []):
                if attr.get("label", "").lower().startswith("warmmiete"):
                    return clean_price_size(attr.get("text"))
    for section in data.get("sections", []):
        if section.get("type") == "ATTRIBUTE_LIST" and section.get("title", "").lower() == "kosten":
            for attr in section.get("attributes", []):
                if attr.get("label", "").lower().startswith("gesamtmiete"):
                    return clean_price_size(attr.get("text"))
    return None


def is_swapflat(data):
    title = next((s.get("title", "") for s in data.get("sections", []) if s.get("title")), "")
    description = next((s.get("text", "") for s in data.get("sections", []) if s.get("type") == "DESCRIPTION"), "")
    top_attrs = [
        attr.get("text", "")
        for s in data.get("sections", []) if s.get("type") == "TOP_ATTRIBUTES"
        for attr in s.get("attributes", [])
    ]
    text_all = title + description + " ".join(top_attrs)
    return "tausch" in text_all.lower()


def is_wbs_required(data):
    for section in data.get("sections", []):
        if section.get("type") == "ATTRIBUTE_LIST":
            for attr in section.get("attributes", []):
                if attr.get("type") == "CHECK" and "Wohnberechtigungsschein erforderlich" in attr.get("label", ""):
                    return True
    return False


def get_token():
    token_url = "https://publicauth.immobilienscout24.de/oauth/token"
    params = {
        "client_id": IMMOSCOUT_CLIENT_ID,
        "grant_type": "client_credentials",
        "client_secret": IMMOSCOUT_CLIENT_SECRET
    }
    response = requests.post(token_url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]


def get_new_ids(headers, published_after):
    print(f"📌 Поиск новых объявлений после {datetime.now(BERLIN_TZ).strftime('%Y-%m-%d %H:%M:%S')} (Берлинское время)")
    url = "https://api.mobile.immobilienscout24.de/search/map/v3"
    params = {
        "geocodes": "/de",
        "realEstateType": "apartmentrent",
        "searchType": "region",
        "sorting": "-firstactivation",
        "pagesize": 30,
        "pagenumber": 1,
        "publishedafter": published_after
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    markers = resp.json().get("markers", [])
    ids = [obj["id"] for marker in markers for obj in marker.get("objects", [])]
    print(f"✅ Найдено {len(ids)} новых объектов: {ids}")
    return ids


def get_expose_details(headers, ids, cursor, conn):
    count = 0
    new_ids = ids

    for obj_id in new_ids:
        try:
            url = f"https://api.mobile.immobilienscout24.de/expose/{obj_id}?adType=RENT"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            media_section = next((s for s in data.get("sections", []) if s.get("type") == "MEDIA"), {})
            photo_urls = [
                m.get("fullImageUrl")
                for m in media_section.get("media", [])
                if m.get("type") == "PICTURE" and m.get("fullImageUrl")
            ][:5]

            addr_section = next((s for s in data.get("sections", []) if s.get("type") == "MAP"), {})
            address = addr_section.get("addressLine1", "") + ", " + addr_section.get("addressLine2", "")
            lat = addr_section.get("location", {}).get("lat")
            lon = addr_section.get("location", {}).get("lng")

            if not lat or not lon:
                if "Die vollständige Adresse" in address:
                    parts = address.split(",", 1)
                    if len(parts) > 1:
                        address = parts[1].strip()
                lat, lon = geocode_address(address)
                if lat and lon:
                    print(f"🌍 Координаты найдены для адреса: '{address}'")
                time.sleep(1)

            attr_section = next((s for s in data.get("sections", []) if s.get("type") == "TOP_ATTRIBUTES"), {})
            price_raw = next((a["text"] for a in attr_section.get("attributes", []) if "€" in a.get("text", "")), None)
            size_raw = next((a["text"] for a in attr_section.get("attributes", []) if "m²" in a.get("text", "")), None)

            price = clean_price_size(price_raw)
            size = clean_price_size(size_raw)
            price_warm = extract_warmmiete(data)
            swapflat = is_swapflat(data)
            wbs_required = is_wbs_required(data)

            listing = {
                "url": f"https://www.immobilienscout24.de/expose/{obj_id}",
                "price": price,
                "price_warm": price_warm,
                "size": size,
                "address": address,
                "lat": lat,
                "lon": lon,
                "swapflat": swapflat,
                "wbs_required": wbs_required,
                "photo_url": ",".join(photo_urls)
            }

            log_listing = listing.copy()
            log_listing["photo_url"] = f"{len(photo_urls)} photos" if photo_urls else "no photos"

            count += 1
            print(f"{count}. 🏠 {log_listing}")
            mark_as_seen(conn, cursor, obj_id, listing)
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ Ошибка при обработке ID {obj_id}: {str(e)}")

    return count > 0


def run():
    conn, cursor = init_db()
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}", **IMMOSCOUT_HEADERS}

        published_after = datetime.now(timezone.utc).isoformat(timespec="seconds")
        ids = get_new_ids(headers, published_after)

        if ids:
            return get_expose_details(headers, ids, cursor, conn)
        else:
            print("🔍 Новых объявлений пока нет.")
            return False

    except Exception as e:
        print(f"🔥 Критическая ошибка: {str(e)}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    run()
