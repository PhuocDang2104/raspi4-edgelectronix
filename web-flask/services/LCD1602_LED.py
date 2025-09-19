import time
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
import redis
import threading
import subprocess
import shutil
import os

# --- CONFIG ---
LED_STATUS = 17       # LED 1: trạng thái drop_detect YES/NO
LED_WARNING = 27      # LED 2: cảnh báo nhiệt độ cao (GPIO27)

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_STATUS, GPIO.OUT)
GPIO.setup(LED_WARNING, GPIO.OUT)

lcd = CharLCD('PCF8574', 0x27)

# Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# --- TTS setup ---
USE_ESPEAK = shutil.which("espeak") is not None
USE_PYTTX3 = False
try:
    import pyttsx3
    USE_PYTTX3 = True
except Exception:
    USE_PYTTX3 = False

# cố gắng chọn analog output (best-effort)
def try_set_analog_output():
    try:
        # legacy method on some Pi OS versions
        os.system("amixer cset numid=3 1 >/dev/null 2>&1")
    except Exception:
        pass

try_set_analog_output()

_engine = None
_engine_lock = threading.Lock()
_last_spoken = {}
COOLDOWN_SECS = 5  # tránh lặp cùng câu trong X giây

def tts_espeak(text):
    try:
        # non-blocking: spawn tiến trình
        subprocess.Popen(["espeak", "-s", "140", text])
    except Exception as e:
        print("❌ espeak failed:", e)

def tts_pyttx3(text):
    global _engine
    with _engine_lock:
        if _engine is None:
            try:
                _engine = pyttsx3.init()
                _engine.setProperty("rate", 150)
            except Exception as e:
                print("❌ pyttsx3 init error:", e)
                _engine = None
        if _engine:
            try:
                _engine.say(text)
                _engine.runAndWait()
            except Exception as e:
                print("❌ pyttsx3 error:", e)

def speak_nonblocking(text):
    def _worker(t):
        if USE_ESPEAK:
            tts_espeak(t)
        elif USE_PYTTX3:
            tts_pyttx3(t)
        else:
            print("⚠️ No TTS backend available. Would say:", t)
    threading.Thread(target=_worker, args=(text,), daemon=True).start()

def can_speak(key):
    now = time.time()
    last = _last_spoken.get(key, 0)
    if now - last >= COOLDOWN_SECS:
        _last_spoken[key] = now
        return True
    return False

# --- ENV / DROP logic ---
# Overheat threshold (độ C) - chỉnh theo nhu cầu
OVERHEAT_TEMP = 31.5

try:
    while True:
        # Đọc dữ liệu môi trường từ Redis
        env_data = r.hgetall("environment_monitor")
        if env_data:
            try:
                temperature = float(env_data.get("temperature", 0))
                humidity = float(env_data.get("humidity", 0))
            except (ValueError, TypeError):
                temperature, humidity = 0, 0
        else:
            temperature, humidity = 0, 0

        # Đọc trạng thái drop từ Redis
        drop_val = r.get("drop_detect_event")
        if drop_val == "1":
            # Bật LED drop
            GPIO.output(LED_STATUS, GPIO.HIGH)

            # Hiển thị cảnh báo trên LCD
            lcd.clear()
            lcd.write_string("DROP DETECTED !!!")
            lcd.crlf()
            lcd.write_string("Pls be careful !")
            # Phát TTS: Drop detected (cooldown áp dụng)
            speak_text = "Drop detected"
            if can_speak(speak_text):
                print("🔊 TTS:", speak_text)
                speak_nonblocking(speak_text)

            time.sleep(5)

            # Sau khi hiển thị cảnh báo thì reset key để tránh lặp lại
            try:
                r.set("drop_detect_event", "0")
            except Exception:
                pass

        else:
            # Tắt LED drop
            GPIO.output(LED_STATUS, GPIO.LOW)

            # LED cảnh báo nhiệt độ cao
            if temperature >= OVERHEAT_TEMP:
                GPIO.output(LED_WARNING, GPIO.HIGH)

                # Phát TTS: Overheat warning (cooldown áp dụng)
                speak_text = "Overheat warning"
                if can_speak(speak_text):
                    print("🔊 TTS:", speak_text)
                    speak_nonblocking(speak_text)

                # Khi quá nhiệt, bạn vẫn có thể hiển thị cảnh báo trên LCD thay vì màn hình bình thường
                lcd.clear()
                lcd.write_string("OVERHEAT WARNING!")
                lcd.crlf()
                lcd.write_string(f"Temp: {temperature:.1f}C")
                time.sleep(3)
            else:
                GPIO.output(LED_WARNING, GPIO.LOW)

                # Hiển thị bình thường: nhiệt + ẩm
                lcd.clear()
                lcd.write_string(f"Temp:      {temperature:.1f}C")
                lcd.crlf()
                lcd.write_string(f"Humid:     {humidity:.1f}%")
                time.sleep(2)

except KeyboardInterrupt:
    lcd.clear()
    GPIO.cleanup()
    print("\nChương trình dừng.")
