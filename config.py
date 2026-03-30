#config.py
API_KEY = "4dddddafa38442bf9db174038251911"
WEATHER_BASE_URL = "https://api.weatherapi.com/v1"


CITIES = [
    "Ludhiana, Punjab, India",
    "Nashik, Maharashtra, India",
    "Sangli, Maharashtra, India",
    "Coimbatore, Tamil Nadu, India",
    "Haveri, Karnataka, India"
]

# Kafka
KAFKA_BOOTSTRAP = "localhost:9092"
HISTORY_TOPIC = "weather-history-topic"
CURRENT_TOPIC = "weather-current-topic"

# Producer settings
BACKFILL_DAYS = 120
CURRENT_FORECAST_DAYS = 5
CURRENT_INTERVAL_HOURS = 1
HISTORY_DAILY_TIME = "00:30"   # HH:MM local time for daily history job

# Postgres (same server, three DBs)
POSTGRES = {
    "host": "localhost",
    "port": 5432,
    "history_db": {
        "host": "localhost",
        "port": 5432,
        "database": "weather_history_db",
        "user": "postgres",
        "password": "Shami@2004"
    },
    "current_db": {
        "host": "localhost",
        "port": 5432,
        "database": "weather_current_db",
        "user": "postgres",
        "password": "Shami@2004"
    },
    "crops_db": {
        "host": "localhost",
        "port": 5432,
        "database": "crops_db",
        "user": "postgres",
        "password": "Shami@2004"
    }
}

# HTTP retry/backoff
HTTP_RETRIES = 4
HTTP_RETRY_SLEEP = 2

TIMEZONE = "Asia/Kolkata"

