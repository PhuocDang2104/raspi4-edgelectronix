#!/usr/bin/env python3
"""
all_12_gpio_on.py
 - Setup 12 GPIO outputs (10 perfume pins + LED_STATUS + LED_WARNING)
 - Bật tất cả cùng lúc (GPIO.HIGH), giữ theo --duration (giây) hoặc đến khi nhấn Enter
 - Yêu cầu RPi.GPIO, dùng BCM numbering. Chạy bằng sudo.
Usage examples:
  sudo python3 all_12_gpio_on.py            # bật tất cả, chờ Enter để tắt
  sudo python3 all_12_gpio_on.py --duration 5   # bật 5 giây rồi tắt
  sudo python3 all_12_gpio_on.py --status-pin 17 --warning-pin 27
"""

import time
import sys
import argparse
import signal
import threading

# ----- Mapping perfumes -> BCM GPIO (your list) -----
PERFUME_GPIO_MAP = {
    "P001": 22,  # alien
    "P030": 23,  # geranium
    "P020": 24,  # bee
    "P047": 25,  # gardenia
    "P049": 5,   # incanto
    "P007": 6,   # amber
    "P017": 12,  # Gucci
    "P045": 13,  # braze
    "P026": 19,  # sexy
    "P005": 26,  # gucci-bamboo
}

# Default pins for LED_STATUS and LED_WARNING (BCM). Bạn có thể override bằng CLI.
DEFAULT_LED_STATUS_PIN = 17
DEFAULT_LED_WARNING_PIN = 27

# stop event để dừng an toàn
stop_event = threading.Event()

def signal_handler(signum, frame):
    print(f"\nReceived signal {signum}, stopping...")
    stop_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_args():
    p = argparse.ArgumentParser(description="Turn ON 12 GPIO pins simultaneously (10 perfume + status+warning). BCM numbering.")
    p.add_argument("--status-pin", type=int, default=DEFAULT_LED_STATUS_PIN,
                   help=f"BCM pin for LED_STATUS (default {DEFAULT_LED_STATUS_PIN})")
    p.add_argument("--warning-pin", type=int, default=DEFAULT_LED_WARNING_PIN,
                   help=f"BCM pin for LED_WARNING (default {DEFAULT_LED_WARNING_PIN})")
    p.add_argument("--duration", type=float, default=None,
                   help="If provided and >0: keep LEDs ON for this many seconds then turn OFF. If omitted: wait for Enter to turn off.")
    p.add_argument("--no-cleanup", action="store_true",
                   help="If set, do not call GPIO.cleanup() on exit (not recommended).")
    return p.parse_args()

def main():
    args = parse_args()

    # Build the full pin list (unique)
    extra_pins = [args.status_pin, args.warning_pin]
    perfume_pins = list(PERFUME_GPIO_MAP.values())
    all_pins = list(dict.fromkeys(perfume_pins + extra_pins))  # preserve order, dedupe if overlap

    # Import RPi.GPIO (mandatory)
    try:
        import RPi.GPIO as GPIO
    except Exception as e:
        print("ERROR: RPi.GPIO không được tìm thấy. Hãy cài trên Raspberry Pi trước khi chạy.", file=sys.stderr)
        print("  sudo apt update && sudo apt install python3-rpi.gpio", file=sys.stderr)
        print("  hoặc: sudo pip3 install RPi.GPIO", file=sys.stderr)
        sys.exit(1)

    # Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    try:
        for pin in all_pins:
            try:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            except Exception as ex:
                print(f"[GPIO Warn] Không thể setup pin {pin}: {ex}", file=sys.stderr)

        print("Các pin sẽ được bật (BCM):", all_pins)
        # Bật tất cả (gần như đồng thời — lập vòng lặp nhanh để set HIGH)
        for pin in all_pins:
            try:
                GPIO.output(pin, GPIO.HIGH)
            except Exception as ex:
                print(f"[GPIO Warn] Lỗi GPIO.output HIGH cho pin {pin}: {ex}", file=sys.stderr)
        print("TẤT CẢ GPIO đã được set HIGH.")

        # Hiện mapping rõ ràng
        print("\nMapping (perfume_id -> BCM pin):")
        for k,v in PERFUME_GPIO_MAP.items():
            print(f"  {k} -> BCM {v}")
        print(f"  LED_STATUS -> BCM {args.status_pin}")
        print(f"  LED_WARNING -> BCM {args.warning_pin}\n")

        # Giữ theo duration hoặc chờ Enter
        if args.duration and args.duration > 0:
            print(f"Giữ ON trong {args.duration} giây...")
            t0 = time.time()
            while time.time() - t0 < args.duration:
                if stop_event.is_set():
                    break
                time.sleep(0.05)
        else:
            print("Đang giữ ON. Nhấn Enter để tắt tất cả hoặc Ctrl+C để hủy.")
            try:
                # non-blocking check for stop_event in case of signal: use input but react to signal
                _ = input()
            except KeyboardInterrupt:
                # signal handler đã set stop_event
                pass

    finally:
        # Tắt tất cả
        print("Tắt tất cả GPIO (set LOW)...")
        try:
            for pin in all_pins:
                try:
                    GPIO.output(pin, GPIO.LOW)
                except Exception as ex:
                    print(f"[GPIO Warn] Lỗi GPIO.output LOW cho pin {pin}: {ex}", file=sys.stderr)
        except Exception:
            pass

        if not args.no_cleanup:
            try:
                GPIO.cleanup()
            except Exception:
                pass
            print("GPIO cleaned up.")
        else:
            print("No cleanup flag set; GPIO.cleanup() skipped.")

if __name__ == "__main__":
    # Khuyến cáo chạy với sudo
    try:
        import os
        if os.geteuid() != 0:
            print("Warning: Nên chạy bằng sudo để truy cập GPIO: sudo python3 all_12_gpio_on.py", file=sys.stderr)
    except Exception:
        pass

    main()
