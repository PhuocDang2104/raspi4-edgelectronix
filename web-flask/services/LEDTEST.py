#!/usr/bin/env python3
# simple_sequence_leds.py
# Chạy tuần tự các LED theo mapping perfume->BCM GPIO.
# Nhấn Ctrl+C để dừng.

import time
import sys

# Mapping perfume ID -> BCM GPIO pin
PERFUME_GPIO_MAP = [
    ("P001", 22),  # alien
    ("P030", 23),  # geranium
    ("P020", 24),  # bee
    ("P047", 25),  # gardenia
    ("P049", 5),   # incanto
    ("P007", 6),   # amber
    ("P017", 12),  # Gucci
    ("P045", 13),  # braze
    ("P026", 19),  # sexy
    ("P005", 26),  # gucci-bamboo
]

# Thời gian mỗi LED sáng (giây)
DURATION = 1.0

# Thời gian giữa các LED (giây)
GAP = 0.1

# Thử import RPi.GPIO; nếu không có, chạy chế độ giả lập (logs)
gpio_available = True
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    for _, pin in PERFUME_GPIO_MAP:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
except Exception as e:
    gpio_available = False
    print("[WARN] RPi.GPIO không khả dụng. Chạy ở chế độ mô phỏng (in log).", file=sys.stderr)

def turn_on(pin):
    if gpio_available:
        GPIO.output(pin, GPIO.HIGH)
    print(f"[ON ] BCM {pin}")

def turn_off(pin):
    if gpio_available:
        GPIO.output(pin, GPIO.LOW)
    print(f"[OFF] BCM {pin}")

def cleanup():
    if gpio_available:
        try:
            GPIO.cleanup()
        except Exception:
            pass
    print("GPIO cleaned up (if available).")

def run_sequence():
    print("Bắt đầu sequence. Nhấn Ctrl+C để dừng.")
    try:
        while True:
            for pid, pin in PERFUME_GPIO_MAP:
                print(f"-> {pid} (BCM {pin}) ON for {DURATION}s")
                turn_on(pin)
                time.sleep(DURATION)
                turn_off(pin)
                time.sleep(GAP)
    except KeyboardInterrupt:
        print("\nĐã dừng bởi người dùng.")
    finally:
        cleanup()

if __name__ == "__main__":
    run_sequence()
