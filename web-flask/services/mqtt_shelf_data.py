# mqtt_shelf_data.py (Desktop) - subscribe CNT + QTY
# CNT -> Redis, QTY -> PostgreSQL
import json
import redis
import psycopg2
import paho.mqtt.client as mqtt

BROKER = "192.168.178.66"       # IP broker (cùng LAN với Raspi)
TOPIC_SHELF = "sensors/shelf"

# ⚙️ PostgreSQL config
POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'admin'
}

# Kết nối PostgreSQL
conn = psycopg2.connect(**POSTGRES_CONFIG)
conn.autocommit = True
cur = conn.cursor()

# Redis client (chỉ để lưu CNT)
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe(TOPIC_SHELF)
    else:
        print("❌ Failed to connect, return code:", rc)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"📥 Received shelf data: {data}")

        # --- Lưu CNT vào Redis ---
        if "counts" in data:
            cnt_str = "CNT:" + ",".join(data["counts"])
            r.set("pick_count_from_mqtt", cnt_str)
            print("💾 Saved CNT to Redis:", cnt_str)

        # --- Ghi QTY vào PostgreSQL ---
        qty = data.get("qty", [])
        if qty:
            qty_str = "QTY:" + ",".join(qty)
            print("📦 Shelf QTY:", qty_str)

            perfume_ids = [
                "P001", "P030", "P007", "P017", "P020",
                "P026", "P005", "P045", "P047", "P049"
            ]

            for pid, stock in zip(perfume_ids, qty):
                cur.execute(
                    """
                    UPDATE shelf_stock
                    SET shelf_stock = %s
                    WHERE perfume_id = %s
                    """,
                    (int(stock), pid)
                )

            print("💾 PostgreSQL updated with new QTY values")

    except Exception as e:
        print("❌ Error parsing or updating:", e)

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_forever()
