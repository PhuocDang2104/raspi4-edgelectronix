#!/usr/bin/env python3
# test_sequence_leds_gpio_output.py
# Chạy tuần tự 10 LED trên Raspberry Pi (BCM numbering).
# Mỗi LED được bật bằng: GPIO.output(LED_STATUS, GPIO.HIGH)
# Hãy chạy bằng sudo: sudo python3 test_sequence_leds_gpio_output.py
#
# Tham số:
#   --duration N   : thời gian mỗi LED ON (giây), mặc định 1.0
#   --gap N        : thời gian OFF giữa các LED (giây), mặc định 0.1
#   --cycles N     : số vòng lặp, 0 = vô hạn (mặc định 0)
#
# Ctrl+C để dừng, script sẽ gọi GPIO.cleanup().

import time
import sys
import argparse
import signal
import threading

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

DEFAULT_DURATION = 1.0
DEFAULT_GAP = 0.1
DEFAULT_CYCLES = 0  # 0 -> infinite

# Mandatory import for Raspberry Pi
try:
    import RPi.GPIO as GPIO
except Exception as e:
    print("ERROR: RPi.GPIO không được tìm thấy. Hãy cài trên Raspberry Pi trước khi chạy.", file=sys.stderr)
    print("  sudo apt update && sudo apt install python3-rpi.gpio", file=sys.stderr)
    print("  hoặc: sudo pip3 install RPi.GPIO", file=sys.stderr)
    sys.exit(1)

# BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup pins
def setup_pins():
    for _, pin in PERFUME_GPIO_MAP:
        try:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        except Exception as ex:
            print(f"[GPIO Warn] Không thể setup pin {pin}: {ex}", file=sys.stderr)

def cleanup():
    try:
        GPIO.cleanup()
    except Exception:
        pass
    print("GPIO cleaned up.")

# stop event để dừng an toàn
stop_event = threading.Event()

def signal_handler(signum, frame):
    print(f"\nReceived signal {signum}, stopping...")
    stop_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_sequence(duration=DEFAULT_DURATION, gap=DEFAULT_GAP, cycles=DEFAULT_CYCLES):
    setup_pins()
    print(f"Starting sequence. duration={duration}s gap={gap}s cycles={'infinite' if cycles==0 else cycles}")
    try:
        loop = 0
        while not stop_event.is_set():
            loop += 1
            for pid, pin in PERFUME_GPIO_MAP:
                if stop_event.is_set():
                    break
                # Use LED_STATUS variable as you requested
                LED_STATUS = pin
                print(f"-> {pid} (BCM {LED_STATUS}) ON for {duration}s")
                try:
                    GPIO.output(LED_STATUS, GPIO.HIGH)   # bật LED
                except Exception as ex:
                    print(f"[GPIO Warn] Lỗi bật pin {LED_STATUS}: {ex}", file=sys.stderr)
                # responsive sleep
                t0 = time.time()
                while time.time() - t0 < duration:
                    if stop_event.is_set():
                        break
                    time.sleep(0.05)
                try:
                    GPIO.output(LED_STATUS, GPIO.LOW)    # tắt LED
                except Exception as ex:
                    print(f"[GPIO Warn] Lỗi tắt pin {LED_STATUS}: {ex}", file=sys.stderr)
                # gap
                t0 = time.time()
                while time.time() - t0 < gap:
                    if stop_event.is_set():
                        break
                    time.sleep(0.05)
            if cycles > 0 and loop >= cycles:
                print(f"Completed {cycles} cycle(s).")
                break
    except Exception as ex:
        print("Lỗi trong run_sequence:", ex, file=sys.stderr)
    finally:
        cleanup()

def parse_args():
    p = argparse.ArgumentParser(description="Simple sequential LED tester using GPIO.output(LED_STATUS, GPIO.HIGH)")
    p.add_argument("--duration", type=float, default=DEFAULT_DURATION, help="Thời gian mỗi LED sáng (s)")
    p.add_argument("--gap", type=float, default=DEFAULT_GAP, help="Khoảng giữa các LED (s)")
    p.add_argument("--cycles", type=int, default=DEFAULT_CYCLES, help="Số vòng lặp (0 = vô hạn)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    # khuyến cáo chạy với sudo
    try:
        import os
        if os.geteuid() != 0:
            print("Warning: Nên chạy bằng sudo để truy cập GPIO: sudo python3 test_sequence_leds_gpio_output.py", file=sys.stderr)
    except Exception:
        pass

    run_sequence(duration=args.duration, gap=args.gap, cycles=args.cycles)
