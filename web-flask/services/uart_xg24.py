import serial
import time

# Mở UART
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

while True:
    # Gửi chuỗi
    ser.write(b'Hello from Pi\n')
    print("Đã gửi: Hello from Pi")

    # Thử đọc dữ liệu
    data = ser.readline().decode('utf-8').strip()
    if data:
        print("Nhận:", data)

    time.sleep(1)
