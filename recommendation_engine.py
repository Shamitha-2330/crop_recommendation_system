# recommendation_engine.py

import json
import psycopg2
from datetime import datetime, timedelta
from config import POSTGRES, CITIES
from dateutil import parser
import traceback

# Maps for parsing
RAIN_MAP = {"low": 5.0, "medium": 20.0, "high": 50.0}
WIND_MAP = {"low": 15.0, "medium": 25.0, "high": 35.0}

# Load crop requirements
with open("crop_requirements.json", "r") as fh:
    CROP_REQ = json.load(fh)


def get_conn_for(cfg):
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"]
    )


def fetch_history_rows(city, days=120):
    conn = get_conn_for(POSTGRES["history_db"])
    cur = conn.cursor()

    start_date = (datetime.utcnow().date() - timedelta(days=days))

    cur.execute("""
        SELECT date, temp_c, humidity, wind_kph, precip_mm, chance_of_rain
        FROM weather_history
        WHERE city = %s AND date >= %s
        ORDER BY date ASC
    """, (city, start_date))

    rows = [{
        "date": r[0],
        "temp_c": r[1],
        "humidity": r[2],
        "wind_kph": float(r[3]) if r[3] else 0.0,
        "precip_mm": float(r[4]) if r[4] else 0.0,
        "chance_of_rain": r[5]
    } for r in cur.fetchall()]

    cur.close()
    conn.close()
    return rows


def fetch_latest_current(city):
    conn = get_conn_for(POSTGRES["current_db"])
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, temp_c, humidity, wind_kph, precip_mm, chance_of_rain, created_at
        FROM weather_current
        WHERE city = %s AND is_forecast = false
        ORDER BY created_at DESC
        LIMIT 1
    """, (city,))

    r = cur.fetchone()
    cur.close()
    conn.close()

    if not r:
        return None

    return {
        "timestamp": r[0],  # actual API timestamp
        "temp_c": r[1],
        "humidity": r[2],
        "wind_kph": float(r[3]) if r[3] else 0.0,
        "precip_mm": float(r[4]) if r[4] else 0.0,
        "chance_of_rain": r[5],
        "created_at": r[6]
    }


def fetch_forecast_rows(city, days=5):
    conn = get_conn_for(POSTGRES["current_db"])
    cur = conn.cursor()

    today = datetime.utcnow().date()
    end_date = today + timedelta(days=days - 1)

    cur.execute("""
        SELECT forecast_date, temp_c, humidity, wind_kph, precip_mm, chance_of_rain
        FROM weather_current
        WHERE city = %s AND is_forecast = true
          AND forecast_date BETWEEN %s AND %s
        ORDER BY forecast_date ASC
    """, (city, today, end_date))

    rows = [{
        "forecast_date": r[0],
        "temp_c": r[1],
        "humidity": r[2],
        "wind_kph": float(r[3]) if r[3] else 0.0,
        "precip_mm": float(r[4]) if r[4] else 0.0,
        "chance_of_rain": r[5]
    } for r in cur.fetchall()]

    cur.close()
    conn.close()
    return rows


def already_processed(city, weather_ts):
    conn = get_conn_for(POSTGRES["crops_db"])
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) 
        FROM crop_recommendations
        WHERE city = %s AND timestamp = %s
    """, (city, weather_ts))

    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    return count > 0


def save_recommendations_batch(city, weather_ts, recs):
    conn = get_conn_for(POSTGRES["crops_db"])
    cur = conn.cursor()

    sql = """
        INSERT INTO crop_recommendations
        (city, timestamp, crop_name, suitability_score,
         heat_stress_risk, fungal_risk, irrigation_advice, reason)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    for r in recs:
        cur.execute(sql, (
            city, weather_ts,
            r["crop"], r["score"],
            r["heat_risk"], r["fungal_risk"],
            r["irrigation"], r["reason"]
        ))

    conn.commit()
    cur.close()
    conn.close()


def parse_rain_need(x):
    if x is None: return 0.0
    if isinstance(x, (int, float)): return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except:
            return RAIN_MAP.get(x.lower(), 0.0)
    return 0.0


def parse_wind_tol(x):
    if x is None: return 999.0
    if isinstance(x, (int, float)): return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except:
            return WIND_MAP.get(x.lower(), 999.0)
    return 999.0


def as_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default


def score_range(value, ideal, good):
    try:
        v = float(value)
    except:
        return 50

    imin, imax = ideal
    gmin, gmax = good

    if imin <= v <= imax:
        return 100
    if gmin <= v <= gmax:
        return 70

    dist = min(abs(v - imin), abs(v - imax))
    return max(0, 70 - dist * 3)


def rainfall_score(need, actual):
    n = parse_rain_need(need)
    a = as_float(actual)

    if n <= 5:
        if a <= 2: return 100
        if a <= 5: return 80
        if a <= 10: return 60
        return 30

    diff = abs(a - n)
    pct = diff / max(n, 1)

    if pct <= 0.20: return 100
    if pct <= 0.50: return 80
    if pct <= 1.0: return 60
    return 30


def wind_score(tol, wind):
    t = parse_wind_tol(tol)
    w = as_float(wind)

    if w <= t: return 100
    if w <= t + 10: return 70
    return 40


def score_row_for_crop(row, req):
    t = score_range(row["temp_c"], req["temp_ideal"], req["temp_good"])
    h = score_range(row["humidity"], req["humidity_ideal"], req["humidity_good"])
    r = rainfall_score(req["rainfall_need"], row["precip_mm"])
    w = wind_score(req["wind_tolerance"], row["wind_kph"])
    return round(t * 0.40 + h * 0.25 + r * 0.20 + w * 0.15)



HIST_WEIGHT = 0.50
FORECAST_WEIGHT = 0.35
CURRENT_WEIGHT = 0.15


def compute_scores_for_city(city):
    hist = fetch_history_rows(city, 120)
    forecast = fetch_forecast_rows(city, 5)
    current = fetch_latest_current(city)

    print(f"[INFO] {city}: history={len(hist)} forecast={len(forecast)} current={'yes' if current else 'no'}")

    if not hist and not forecast and not current:
        return None, None

    recs = []

    for crop, req in CROP_REQ.items():
        try:
            hist_avg = (sum(score_row_for_crop(r, req) for r in hist) / len(hist)) if hist else None
            fore_avg = (sum(score_row_for_crop(r, req) for r in forecast) / len(forecast)) if forecast else None

            if current:
                cur_row = {
                    "temp_c": current["temp_c"],
                    "humidity": current["humidity"],
                    "wind_kph": current["wind_kph"],
                    "precip_mm": current["precip_mm"]
                }
                cur_score = score_row_for_crop(cur_row, req)
            else:
                cur_score = None

            comps = []
            weights = []

            if hist_avg is not None:
                comps.append(hist_avg)
                weights.append(HIST_WEIGHT)

            if fore_avg is not None:
                comps.append(fore_avg)
                weights.append(FORECAST_WEIGHT)

            if cur_score is not None:
                comps.append(cur_score)
                weights.append(CURRENT_WEIGHT)

            if comps:
                total = sum(weights)
                final = sum(v * (w / total) for v, w in zip(comps, weights))
                final_score = round(final)
            else:
                final_score = 0

            temp_r = current["temp_c"] if current else hist[-1]["temp_c"]
            hum_r = current["humidity"] if current else hist[-1]["humidity"]
            precip_r = current["precip_mm"] if current else hist[-1]["precip_mm"]
            chance_r = current["chance_of_rain"] if current else 0

            heat_risk = "High" if temp_r > 37 and hum_r > 70 else "Low"
            fungal_risk = "High" if hum_r > 80 and temp_r > 25 else "Low"

            if chance_r > 60:
                irrigation = "Postpone irrigation — high chance of rain"
            elif hum_r < 40:
                irrigation = "Irrigate Now — low humidity"
            else:
                irrigation = "Normal irrigation"

            reason = (
                f"HistAvg:{hist_avg}, ForecastAvg:{fore_avg}, "
                f"Current:{cur_score}, Final:{final_score}"
            )

            recs.append({
                "crop": crop,
                "score": final_score,
                "heat_risk": heat_risk,
                "fungal_risk": fungal_risk,
                "irrigation": irrigation,
                "reason": reason
            })

        except Exception as e:
            print(f"[ERROR] scoring {crop} for {city}: {e}")
            traceback.print_exc()

    
    if current:
        weather_ts = current["timestamp"].astimezone()
        weather_ts = weather_ts.replace(minute=0, second=0, microsecond=0)
    else:
        weather_ts = datetime.now().astimezone().replace(minute=0, second=0, microsecond=0)

    return weather_ts, recs




def main():
    print("\n🌾 Recommendation Engine (batch) starting...\n")

    for city in CITIES:
        try:
            weather_ts, recs = compute_scores_for_city(city)
            if not weather_ts or not recs:
                print(f"[SKIP] No recommendations for {city}")
                continue

            if already_processed(city, weather_ts):
                print(f"[SKIP] already processed recommendations for {city} @ {weather_ts}")
                continue

            save_recommendations_batch(city, weather_ts, recs)
            print(f"[SAVED] {len(recs)} recommendations for {city} @ {weather_ts}")

        except Exception as e:
            print(f"[FATAL] while processing {city}: {e}")
            traceback.print_exc()

    print("\n✅ Recommendation batch complete.\n")


if __name__ == "__main__":
    main()
