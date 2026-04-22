# IoT Alarm Service 

## Overview

This project implements a **stateful alarm service** for an IoT Gateway.
It processes real-time sensor data via MQTT and triggers alarms based on configurable rules.

---

##  Features

* MQTT-based data ingestion
* Threshold & Conditional alarms
* Stateful processing using SQLite
* Alarm publishing via MQTT
* Persistent storage across reboot
* Scalable and modular design

---

##  Architecture

* MQTT Broker (Mosquitto)
* Python Rule Engine
* SQLite for persistence
* CLI (optional)

---

## How It Works

1. Sensors publish data to MQTT topics
2. Service subscribes to `sensor/#`
3. Rules are evaluated
4. Alarm triggered if condition + duration satisfied
5. Alarm published to `alarms/{alarm_id}`

---

## Example Rule

Temperature > 24°C for 60 seconds

---

##  How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Start Mosquitto

```
mosquitto
```

### 3. Run service

```
python main.py
```

### 4. Publish test data

```
mosquitto_pub -h localhost -t sensor/temp -m "{\"value\": 30}"
```

---

## Database

SQLite is used for:

* Alarm rules
* Alarm state
* Alarm history

---

## Assumptions

* Sensors publish valid JSON
* MQTT broker runs locally
* Time-based evaluation depends on incoming data


