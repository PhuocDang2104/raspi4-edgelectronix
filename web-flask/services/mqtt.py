# mqtt.py (Raspi4) - publish env + poll Redis key drop_detect_event -> publish MQTT event once
import time
import threading
import json
import redis
import paho.mqtt.client as mqtt

BROKER = "192.168.67.66"         #có thể thay đổi theo ngày, check trước ip
TOPIC_ENV = "sensors/env"
TOPIC_EVENTS = "sensors/events"   # topic để gửi event drop tới laptop

# MQTT client
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

# Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def env_publisher():
    while True:
        try:
            env_data = r.hgetall("environment_monitor")
            if env_data:
                msg = f"{env_data.get('temperature')}|{env_data.get('humidity')}"
                client.publish(TOPIC_ENV, msg)
                print("📤 Publish env:", msg)
        except Exception as e:
            print("❌ Env publisher error:", e)
        time.sleep(2)

def drop_poller():
    while True:
        try:
            val = r.get('drop_detect_event')
            if val is not None and str(val) == "1":
                event = {
                    "event": "drop_detected",
                    "timestamp": int(time.time())
                }
                payload = json.dumps(event)
                client.publish(TOPIC_EVENTS, payload)
                print("📤 Published drop event to MQTT:", payload)

                # reset/delete key so we don't republish repeatedly
                try:
                    r.delete('drop_detect_event')
                except Exception as e:
                    # fallback: set to "0"
                    try:
                        r.set('drop_detect_event', "0")
                    except Exception:
                        pass
        except Exception as e:
            print("❌ Drop poller error:", e)
        time.sleep(1)  # poll every 1s (tăng giảm tùy nhu cầu)

if __name__ == "__main__":
    try:
        t1 = threading.Thread(target=env_publisher, daemon=True)
        t2 = threading.Thread(target=drop_poller, daemon=True)
        t1.start()
        t2.start()

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