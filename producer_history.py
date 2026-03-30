# producer_history.py
import time, requests, json
from datetime import datetime, timedelta
from utils.kafka_helper import get_producer
from config import *

producer = get_producer()

def fetch_history(city, dt_str):
    url = f"{WEATHER_BASE_URL}/history.json?key={API_KEY}&q={city}&dt={dt_str}"
    for attempt in range(1, HTTP_RETRIES+1):
        try:
            resp = requests.get(url, timeout=12)
            data = resp.json()
            if "error" in data:
                print("[API_ERROR]", data["error"])
                return None
            return data
        except Exception as e:
            print(f"[ERROR] fetch_history {city} {dt_str} attempt {attempt}: {e}")
            time.sleep(HTTP_RETRY_SLEEP)
    return None

def flatten_and_send(city, api_data, dt_str):
    try:
        day = api_data["forecast"]["forecastday"][0]["day"]
    except Exception as e:
        print("[SKIP] bad response for", city, dt_str, e)
        return
    payload = {
        "type": "history",
        "city": city,
        "date": dt_str,
        "temp_c": day.get("avgtemp_c"),
        "humidity": day.get("avghumidity"),
        "wind_kph": day.get("maxwind_kph"),
        "precip_mm": day.get("totalprecip_mm"),
        "chance_of_rain": day.get("daily_chance_of_rain", 0),
        "condition_text": day.get("condition", {}).get("text", ""),
        "source": "weatherapi_history"
    }
    producer.send(HISTORY_TOPIC, payload)

def run_backfill(days=BACKFILL_DAYS):
    today = datetime.utcnow().date()
    start = today - timedelta(days=days)
    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    for city in CITIES:
        print("Backfilling:", city)
        for dt in dates:
            data = fetch_history(city, dt)
            if data:
                flatten_and_send(city, data, dt)
            time.sleep(1)
    producer.flush()
    print("Backfill done")

if __name__ == "__main__":
    run_backfill()
