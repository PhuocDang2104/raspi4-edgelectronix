# mqtt_customer_data.py
# Raspi4 - publish customer form data từ Redis sang MQTT

import time
import json
import redis
import paho.mqtt.client as mqtt

# ⚙️ MQTT config
BROKER = "192.168.162.66"        # nhớ check lại IP broker trước khi chạy
TOPIC_CUSTOMER = "customer/data" # topic publish form_input

# ⚙️ MQTT client
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

# ⚙️ Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def publish_customer_data():
    """Poll Redis key uart_outgoing_message và publish sang MQTT."""
    last_value = None
    while True:
        try:
            # Lấy dữ liệu từ Redis
            value = r.get("uart_outgoing_message")
            if value and value != last_value:
                try:
                    data = json.loads(value)
                except json.JSONDecodeError:
                    print("⚠️ Redis value không phải JSON hợp lệ, bỏ qua.")
                    last_value = value
                    time.sleep(1)
                    continue

                print("\n📤 Gửi dữ liệu customer form qua MQTT:")
                for key, val in data.items():
                    print(f"  {key}: {val}")

                # Publish lên MQTT
                client.publish(TOPIC_CUSTOMER, json.dumps(data))
                last_value = value

        except Exception as e:
            print(f"❌ Lỗi khi đọc Redis hoặc publish MQTT: {e}")

        time.sleep(1)

if __name__ == "__main__":
    print("🚀 MQTT Customer Data Service đang chạy...")
    publish_customer_data()