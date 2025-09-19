# mqtt_rating.py (Raspi4) - publish ratings từ Redis lên MQTT
import time
import json
import redis
import paho.mqtt.client as mqtt
import subprocess
import random

BROKER = "192.168.67.66"       # Đặt IP của broker (raspi chạy broker)
TOPIC_RATING = "sensors/ratings"

# MQTT client setup
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

# Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Các mẫu câu lịch sự (business polite) để TTS đọc sau khi nhận rating
TTS_PHRASES = [
    "Thank you for your feedback, we truly appreciate your opinion.",
    "Thank you for taking the time to rate our product.",
    "We sincerely appreciate your feedback. Thank you.",
    "Thank you — your input helps us improve our service.",
    "Many thanks for your review; we value your opinion.",
    "We appreciate your time and feedback. Thank you very much.",
    "Thank you for your rating. We strive to do even better.",
    "Sincerely thank you for your valuable feedback.",
    "Thanks for your feedback. We appreciate your support.",
    "Your review is appreciated. Thank you for helping us improve."
]

def speak_nonblocking(text: str):
    """Gọi espeak non-blocking với volume max (amplitude=200) và giọng tiếng Anh nữ."""
    try:
        subprocess.Popen([
            "espeak",
            "-s", "150",
            "-a", "200",
            "-v", "en+f3",
            text
        ])
    except Exception as e:
        print(f"❌ TTS error: {e}")

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

                # Sau khi publish thành công (hoặc ít nhất đã pop), phát 1 câu TTS random lịch sự
                try:
                    tts = random.choice(TTS_PHRASES)
                    print(f"🔊 TTS: {tts}")
                    speak_nonblocking(tts)
                except Exception as e:
                    print(f"❌ Error invoking TTS: {e}")

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
