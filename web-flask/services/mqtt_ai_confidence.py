#!/usr/bin/env python3
import time
import json
import redis
import paho.mqtt.client as mqtt

BROKER = "192.168.67.66"         # thay theo IP broker thực tế
TOPIC_CONF = "ai/confidence"

# MQTT client
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

# Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

print("🚀 mqtt_ai_confidence started...")

last_conf = None

try:
    while True:
        try:
            conf = r.get("uart_model_confidence")
            if conf is not None:
                # chỉ publish nếu giá trị mới khác lần trước
                if conf != last_conf:
                    payload = {"confidence": float(conf)}
                    client.publish(TOPIC_CONF, json.dumps(payload))
                    print(f"[MQTT] Published {payload} -> {TOPIC_CONF}")
                    last_conf = conf
        except Exception as e:
            print("Lỗi Redis/MQTT:", e)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Ngắt chương trình.")
finally:
    client.loop_stop()
    client.disconnect()
