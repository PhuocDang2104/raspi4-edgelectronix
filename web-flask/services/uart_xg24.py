import serial, time

ser = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)

while True:
    ser.write(b"ping\n")
    time.sleep(0.5)
    data = ser.readline()
    if data:
        print("RX:", data.decode().strip())