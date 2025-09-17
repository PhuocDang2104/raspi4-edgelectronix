# mqtt_shelf_data.py (Raspi4) - publish CNT + QTY từ Redis
import time
import threading
import json
import redis
import paho.mqtt.client as mqtt

BROKER = "192.168.67.66"       # ⚠️ check lại IP broker mỗi lần chạy
TOPIC_SHELF = "sensors/shelf"   # topic gửi dữ liệu kệ

# MQTT client
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

# Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def shelf_publisher():
    while True:
        try:
            cnt = r.get("pick_count_from_udp")
            qty = r.get("pick_qty_from_udp")

            if cnt or qty:
                data = {
                    "counts": cnt.split(",") if cnt else [],
                    "qty": qty.split(",") if qty else [],
                    "timestamp": int(time.time())
                }
                payload = json.dumps(data)
                client.publish(TOPIC_SHELF, payload)
                print("📤 Publish shelf data:", payload)
        except Exception as e:
            print("❌ Shelf publisher error:", e)
        time.sleep(2)  # mỗi 2s gửi một lần

if __name__ == "__main__":
    try:
        t = threading.Thread(target=shelf_publisher, daemon=True)
        t.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
