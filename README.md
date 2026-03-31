# 🌾 Real-Time Crop Recommendation System for Indian Agriculture

## 📌 Overview

This project presents a **Real-Time Agriculture Intelligence System** that helps farmers make **data-driven crop decisions** using weather analytics.

Agriculture in India is highly dependent on environmental factors like temperature, humidity, rainfall, and wind speed. Traditional decision-making often leads to crop loss due to unpredictable weather.

This system solves that by combining:

* 🌡️ Real-time weather data
* 📅 Short-term forecast
* 📊 120 days historical data

 It provides **accurate crop recommendations, risk analysis, and irrigation advice**.

---

## 🚀 Key Features

* Real-time weather ingestion using WeatherAPI
* Apache Kafka-based streaming pipeline
* Historical + Current + Forecast analysis
* Crop suitability scoring (0–100)
* Heat stress risk detection
* Fungal infection risk detection
* Smart irrigation recommendations
* Interactive dashboard using Apache Superset

---

## 🏗️ System Architecture

```
WeatherAPI
   ↓
Kafka Producers (History + Current + Forecast)
   ↓
Kafka Topics
   ↓
Kafka Consumer
   ↓
PostgreSQL Database
   ↓
Crop Recommendation Engine
   ↓
Apache Superset Dashboard
```

---

##  Recommendation Logic

The system evaluates crops using a weighted scoring model:

```
Final Score =
(0.50 × Historical Score) +
(0.35 × Forecast Score) +
(0.15 × Current Score)
```

### 🔍 Inputs:

* Last 120 days historical weather
* Current weather conditions
* 5-day forecast data
* Crop requirement dataset

###  Outputs:

* Crop Suitability Score (0–100)
* Heat Stress Risk (Low / High)
* Fungal Risk (Low / High)
* Irrigation Advice

---

## 📊 Metrics Displayed

### 📌 Descriptive Metrics

* Temperature (°C)
* Humidity (%)
* Wind Speed (km/h)
* Rainfall Probability (%)

### 📌 Predictive Metrics

* Rainfall Forecast (Next 5 Days)
* Crop Suitability Score
* Heat Stress Index
* Fungal Risk
* Irrigation Advice

---

## 🛠️ Tech Stack

| Layer         | Technology      |
| ------------- | --------------- |
| Data Source   | WeatherAPI      |
| Streaming     | Apache Kafka    |
| Backend       | Python          |
| Database      | PostgreSQL      |
| Visualization | Apache Superset |
| OS            | Ubuntu          |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Shamitha-2330/Real-Time_crop_recommendation_system
cd Real-Time_crop_recommendation_system
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Start Kafka & Zookeeper

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

### 4️⃣ Create Kafka Topics

```bash
kafka-topics.sh --create --topic weather-history-topic --bootstrap-server localhost:9092
kafka-topics.sh --create --topic weather-current-topic --bootstrap-server localhost:9092
```

### 5️⃣ Run Producers

```bash
python scheduler.py
python producer_history.py
python producer_current.py
```

### 6️⃣ Run Consumer

```bash
python consumer.py
```

### 7️⃣ Run Recommendation Engine

```bash
python recommendation_engine.py
```

### 8️⃣ Start Apache Superset

```bash
superset run -p 8088
```
---

## 📂 Project Structure

```
├── producer_history.py
├── producer_current.py
├── consumer.py
├── scheduler.py
├── recommendation_engine.py
├── crop_requirements.json
├── utils/db_helper.py
├── utils/kafka_helper.py
├── data/cities.json
├── db/schema.sql
├── config.py
├── superset_config.py
├── requirements.txt
└── README.md
```

---

## 📸 Screenshots

<img width="739" height="655" alt="image" src="https://github.com/user-attachments/assets/bd8895f6-6076-4b78-9956-dc652bc63284" />

<img width="739" height="655" alt="image" src="https://github.com/user-attachments/assets/d99c0235-3fb8-4a94-a89b-9bc3e8f6e1ee" />

<img width="739" height="655" alt="image" src="https://github.com/user-attachments/assets/abf515fa-78b4-46fd-b123-8cdb0dc8581b" />

---

## 🎯 Use Cases

*  Smart crop selection
*  Efficient irrigation planning
*  Risk prediction (heat & fungal)
*  Data-driven agriculture decisions

---

## 🚧 Future Improvements

*  Machine Learning-based prediction model
*  Mobile application for farmers
*  Multi-language support
*  Integration with soil & satellite data

---
