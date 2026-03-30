CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    timestamp TIMESTAMP,
    temp_c FLOAT,
    humidity FLOAT,
    wind_kph FLOAT,
    precip_mm FLOAT,
    chance_of_rain INT,
    condition_text VARCHAR(100),
    is_forecast BOOLEAN,
    forecast_date DATE,
    source VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS crop_recommendations (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    timestamp TIMESTAMP,
    crop_name VARCHAR(50),
    suitability_score INT,
    heat_stress_risk VARCHAR(20),
    fungal_risk VARCHAR(20),
    irrigation_advice VARCHAR(50),
    reason TEXT
);

-- 1) Create the three databases (run in psql as postgres superuser)
CREATE DATABASE weather_history_db;
CREATE DATABASE weather_current_db;
-- if you already have crops_db, skip creating
-- CREATE DATABASE crops_db;

-- 2) Connect to weather_history_db and create weather_history table
\c weather_history_db

CREATE TABLE weather_history (
  id SERIAL PRIMARY KEY,
  city TEXT NOT NULL,
  date DATE NOT NULL,          -- historical date (no time)
  temp_c REAL,
  humidity INTEGER,
  wind_kph REAL,
  precip_mm REAL,
  chance_of_rain INTEGER,
  condition_text TEXT,
  source TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(city, date)          -- avoid duplicates
);

-- 3) Connect to weather_current_db and create weather_current table
\c weather_current_db

CREATE TABLE weather_current (
  id SERIAL PRIMARY KEY,
  city TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,   -- precise date+time (today)
  temp_c REAL,
  humidity INTEGER,
  wind_kph REAL,
  precip_mm REAL,
  chance_of_rain INTEGER,
  condition_text TEXT,
  is_forecast BOOLEAN NOT NULL DEFAULT false,
  forecast_date DATE,               -- for forecast rows (date only)
  source TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(city, forecast_date, is_forecast)  -- ensures forecast/current upsert correctness
);

-- 4) crop_recommendations table (in crops_db) - if not present
\c crops_db

CREATE TABLE IF NOT EXISTS crop_recommendations (
  id SERIAL PRIMARY KEY,
  city TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,  -- when recommendation generated (or weather_ts)
  crop_name TEXT NOT NULL,
  suitability_score INTEGER,
  heat_stress_risk TEXT,
  fungal_risk TEXT,
  irrigation_advice TEXT,
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Index to speed lookups by city/timestamp
CREATE INDEX IF NOT EXISTS idx_croprec_city_ts ON crop_recommendations(city, timestamp);
