import time
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
import redis

# --- CONFIG ---
LED_STATUS = 17       # LED 1: trạng thái drop_detect YES/NO
LED_WARNING = 27      # LED 2: cảnh báo nhiệt độ cao (GPIO27)

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_STATUS, GPIO.OUT)
GPIO.setup(LED_WARNING, GPIO.OUT)

lcd = CharLCD('PCF8574', 0x27)

# Redis client
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

try:
    while True:
        # Đọc dữ liệu môi trường từ Redis
        env_data = r.hgetall("environment_monitor")
        if env_data:
            try:
                temperature = float(env_data.get("temperature", 0))
                humidity = float(env_data.get("humidity", 0))
            except ValueError:
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
            lcd.write_string("Pls be careful!")
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
            if temperature >= 31.5:
                GPIO.output(LED_WARNING, GPIO.HIGH)
            else:
                GPIO.output(LED_WARNING, GPIO.LOW)

            # Hiển thị bình thường: nhiệt + ẩm
            lcd.clear()
            lcd.write_string(f"Temp:{temperature:.1f}C")
            lcd.crlf()
            lcd.write_string(f"Humid:{humidity:.1f}%")
            time.sleep(2)

except KeyboardInterrupt:
    lcd.clear()
    GPIO.cleanup()
    print("\nChương trình dừng.")
