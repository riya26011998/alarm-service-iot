import time
import json
import sqlite3
import paho.mqtt.client as mqtt

conn = sqlite3.connect("alarms.db", check_same_thread=False)
print("Database created at local folder")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS rules (
    alarm_id TEXT PRIMARY KEY,
    sensor_id TEXT,
    operator TEXT,
    threshold REAL,
    duration INTEGER,
    shunt_sensor TEXT,
    shunt_operator TEXT,
    shunt_threshold REAL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO rules VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "test",
    "sensor/temp",
    ">",
    24,
    60,
    None,
    None,
    None
))


cursor.execute("""
CREATE TABLE IF NOT EXISTS state (
    alarm_id TEXT,
    start_time INTEGER,
    active INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    alarm_id TEXT,
    triggered_at INTEGER,
    cleared_at INTEGER
)
""")

conn.commit()
print("Tables created")

conn.commit()
latest_values = {}  # cache latest sensor values

def compare(val, op, threshold):
    if op == ">": return val > threshold
    if op == "<": return val < threshold
    if op == "==": return val == threshold
    return False

def evaluate_rule(rule, ts):
    alarm_id, sensor, op, threshold, duration, shunt_sensor, shunt_op, shunt_th = rule

    if sensor not in latest_values:
        return

    value = latest_values[sensor]

    primary = compare(value, op, threshold)

    shunt_ok = True
    if shunt_sensor:
        if shunt_sensor not in latest_values:
            return
        shunt_val = latest_values[shunt_sensor]
        shunt_ok = compare(shunt_val, shunt_op, shunt_th)

    if primary and shunt_ok:
        cursor.execute("SELECT start_time FROM state WHERE alarm_id=?", (alarm_id,))
        row = cursor.fetchone()

        if not row:
            cursor.execute("INSERT INTO state VALUES (?, ?, ?)", (alarm_id, ts, 0))
            conn.commit()
            return

        start_time = row[0]

        if ts - start_time >= duration:
            print(f" Alarm Triggered: {alarm_id}")
            client.publish(f"alarms/{alarm_id}", json.dumps({"status": "TRIGGERED"}))

    else:
        cursor.execute("DELETE FROM state WHERE alarm_id=?", (alarm_id,))
        conn.commit()

def on_message(client, userdata, msg):
    global latest_values

    data = json.loads(msg.payload.decode())
    value = data["value"]
    print(value)
    latest_values[msg.topic] = value
    ts = int(time.time())

    cursor.execute("SELECT * FROM rules")
    rules = cursor.fetchall()

    for rule in rules:
        evaluate_rule(rule, ts)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("127.0.0.1", 1883)
client.subscribe("sensor/#")

client.loop_forever()
