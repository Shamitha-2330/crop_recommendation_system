# producer_current.py
import time, requests, json
from datetime import datetime
from utils.kafka_helper import get_producer
from config import *

producer = get_producer()

def fetch_current_forecast(city):
    url = f"{WEATHER_BASE_URL}/forecast.json?key={API_KEY}&q={city}&days={CURRENT_FORECAST_DAYS}"
    for attempt in range(1, HTTP_RETRIES+1):
        try:
            resp = requests.get(url, timeout=12)
            data = resp.json()
            if "error" in data:
                print("[API_ERROR]", data["error"])
                return None
            return data
        except Exception as e:
            print(f"[ERROR] fetch_current_forecast {city} attempt {attempt}: {e}")
            time.sleep(HTTP_RETRY_SLEEP)
    return None

def flatten_current(city, api_data):
    cur = api_data.get("current", {})
    ts = cur.get("last_updated") or datetime.utcnow().isoformat()
    return {
        "type": "current",
        "city": city,
        "timestamp": ts,
        "temp_c": cur.get("temp_c"),
        "humidity": cur.get("humidity"),
        "wind_kph": cur.get("wind_kph"),
        "precip_mm": cur.get("precip_mm", 0.0),
        "chance_of_rain": cur.get("chance_of_rain", 0),
        "condition_text": cur.get("condition", {}).get("text", ""),
        "is_forecast": False,
        "forecast_date": None,
        "source": "weatherapi_current"
    }

def flatten_forecast(city, forecast_day):
    date = forecast_day.get("date")
    day = forecast_day.get("day", {})
    return {
        "type": "current",
        "city": city,
        "timestamp": datetime.utcnow().isoformat(),
        "temp_c": day.get("avgtemp_c"),
        "humidity": day.get("avghumidity"),
        "wind_kph": day.get("maxwind_kph"),
        "precip_mm": day.get("totalprecip_mm"),
        "chance_of_rain": day.get("daily_chance_of_rain", 0),
        "condition_text": day.get("condition", {}).get("text", ""),
        "is_forecast": True,
        "forecast_date": date,
        "source": "weatherapi_forecast"
    }

def run_once():
    for city in CITIES:
        print("Fetching current+forecast for", city)
        data = fetch_current_forecast(city)
        if not data:
            continue
        producer.send(CURRENT_TOPIC, flatten_current(city, data))
        for f in data.get("forecast", {}).get("forecastday", []):
            producer.send(CURRENT_TOPIC, flatten_forecast(city, f))
        time.sleep(1)
    producer.flush()
    print("Current+forecast run complete")

if __name__ == "__main__":
    run_once()
