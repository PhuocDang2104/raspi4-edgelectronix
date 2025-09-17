# mqtt_rating.py (Raspi4) - publish ratings từ Redis lên MQTT
import time
import json
import redis
import paho.mqtt.client as mqtt

BROKER = "192.168.67.66"       # Đặt IP của broker (raspi chạy broker)
TOPIC_RATING = "sensors/ratings"

# MQTT client setup
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

# Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def publish_ratings():
    print("🚀 Rating publisher started...")
    while True:
        try:
            # Lấy entry đầu tiên trong Redis list "ratings"
            entry = r.lpop("ratings")
            if entry:
                try:
                    rating_data = json.loads(entry)
                except Exception:
                    print("⚠️ Invalid JSON in Redis:", entry)
                    continue

                payload = json.dumps(rating_data)
                client.publish(TOPIC_RATING, payload)
                print("📤 Published rating → MQTT:", payload)
            else:
                # Nếu không có dữ liệu mới thì nghỉ 1 chút
                time.sleep(1)
        except Exception as e:
            print("❌ Error publishing rating:", e)
            time.sleep(2)

if __name__ == "__main__":
    try:
        publish_ratings()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()
