import redis
import time
import paho.mqtt.client as mqtt

# MQTT broker (cài trên Raspi hoặc Desktop, miễn trong LAN)
BROKER = "192.168.1.66"   # IP của broker (broker chạy trên Raspi -> dùng IP Raspi)
TOPIC = "sensors/env"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

while True:
    env_data = r.hgetall("environment_monitor")
    if env_data:
        message = f"{env_data.get('temperature')}|{env_data.get('humidity')}"
        client.publish(TOPIC, message)
        print("📤 Publish:", message)
    time.sleep(2)
