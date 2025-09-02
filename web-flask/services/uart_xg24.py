import serial
import threading

# Mở UART
ser = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)

def read_from_uart():
    """Luồng đọc UART và in ra màn hình"""
    while True:
        data = ser.readline().decode(errors="ignore").strip()
        if data:
            print(f"\nRX: {data}")

# Tạo thread để đọc liên tục
t = threading.Thread(target=read_from_uart, daemon=True)
t.start()

print("UART terminal started. Gõ gì sẽ gửi qua UART. (Ctrl+C để thoát)")
try:
    while True:
        msg = input("> ")
        if msg:
            ser.write((msg + "\n").encode())
except KeyboardInterrupt:
    print("\nThoát terminal.")
    ser.close()
