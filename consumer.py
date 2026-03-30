# consumer.py
import json
from utils.kafka_helper import get_consumer
from utils.db_helper import get_conn_history, get_conn_current
from config import HISTORY_TOPIC, CURRENT_TOPIC
from datetime import datetime

consumer = get_consumer([HISTORY_TOPIC, CURRENT_TOPIC], group_id="db-writer-group")

def insert_history(row):
    conn = get_conn_history()
    cur = conn.cursor()

    sql = """
    INSERT INTO weather_history
      (city, date, temp_c, humidity, wind_kph, precip_mm,
       chance_of_rain, condition_text, source)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (city, date) DO UPDATE SET
       temp_c = EXCLUDED.temp_c,
       humidity = EXCLUDED.humidity,
       wind_kph = EXCLUDED.wind_kph,
       precip_mm = EXCLUDED.precip_mm,
       chance_of_rain = EXCLUDED.chance_of_rain,
       condition_text = EXCLUDED.condition_text,
       source = EXCLUDED.source;
    """

    cur.execute(sql, (
        row["city"],
        row["date"],
        row["temp_c"],
        row["humidity"],
        row["wind_kph"],
        row["precip_mm"],
        row["chance_of_rain"],
        row["condition_text"],
        row["source"]
    ))

    conn.commit()
    cur.close()
    conn.close()



def upsert_current(row):
    conn = get_conn_current()
    cur = conn.cursor()

    sql = """
    INSERT INTO weather_current
      (city, timestamp, temp_c, humidity, wind_kph, precip_mm,
       chance_of_rain, condition_text, is_forecast, forecast_date, source)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (city) WHERE is_forecast = false
    DO UPDATE SET
       timestamp = EXCLUDED.timestamp,
       temp_c = EXCLUDED.temp_c,
       humidity = EXCLUDED.humidity,
       wind_kph = EXCLUDED.wind_kph,
       precip_mm = EXCLUDED.precip_mm,
       chance_of_rain = EXCLUDED.chance_of_rain,
       condition_text = EXCLUDED.condition_text,
       source = EXCLUDED.source;
    """

    cur.execute(sql, (
        row["city"],
        row["timestamp"],
        row["temp_c"],
        row["humidity"],
        row["wind_kph"],
        row["precip_mm"],
        row["chance_of_rain"],
        row["condition_text"],
        False,       # is_forecast
        None,        # forecast_date
        row["source"]
    ))

    conn.commit()
    cur.close()
    conn.close()

def upsert_forecast(row):
    conn = get_conn_current()
    cur = conn.cursor()

    sql = """
    INSERT INTO weather_current
      (city, timestamp, temp_c, humidity, wind_kph, precip_mm,
       chance_of_rain, condition_text, is_forecast, forecast_date, source)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (city, forecast_date) WHERE is_forecast = true
    DO UPDATE SET
       temp_c = EXCLUDED.temp_c,
       humidity = EXCLUDED.humidity,
       wind_kph = EXCLUDED.wind_kph,
       precip_mm = EXCLUDED.precip_mm,
       chance_of_rain = EXCLUDED.chance_of_rain,
       condition_text = EXCLUDED.condition_text,
       source = EXCLUDED.source;
    """

    cur.execute(sql, (
        row["city"],
        row["timestamp"],
        row["temp_c"],
        row["humidity"],
        row["wind_kph"],
        row["precip_mm"],
        row["chance_of_rain"],
        row["condition_text"],
        True,                      
        row["forecast_date"],     
        row["source"]
    ))

    conn.commit()
    cur.close()
    conn.close()



print("[CONSUMER] listening to:", HISTORY_TOPIC, CURRENT_TOPIC)

for msg in consumer:
    try:
        row = msg.value

        if msg.topic == HISTORY_TOPIC:
            if not row.get("date"):
                print("[SKIP] Missing date:", row)
                continue

            insert_history(row)
            print("[HISTORY] saved", row["city"], row["date"])
            continue

        if msg.topic == CURRENT_TOPIC:

            if row["is_forecast"] is True:
                if not row.get("forecast_date"):
                    print("[SKIP] Forecast missing forecast_date:", row)
                    continue

                upsert_forecast(row)
                print("[FORECAST] upserted", row["city"], row["forecast_date"])

            else:
                upsert_current(row)
                print("[CURRENT] upserted", row["city"], row["timestamp"])

    except Exception as e:
        print("[ERROR] consumer loop:", e)
        continue
