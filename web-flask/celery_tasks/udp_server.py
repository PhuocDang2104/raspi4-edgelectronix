import redis
import socket
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

UDP_IP = "::"
UDP_PORT = 12345

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("📡 Listening on UDP port", UDP_PORT)

# Lưu địa chỉ 2 con EFR32
addr1 = None
addr2 = None

while True:
    #1. Check nếu có dữ liệu gửi từ EFR32
    sock.settimeout(0.5)  # không block vĩnh viễn
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        print("Received from", addr, ":", message)
        # Gán thiết bị vào slot
        if addr1 is None or addr == addr1:
            addr1 = addr
            redis_client.set('selected_perfume_id_from_udp', message)
            print(f"✅ Set Redis key 'selected_perfume_id_from_udp': {message}")

        elif addr2 is None or addr == addr2:
            addr2 = addr
            redis_client.set('environment_monitor', message)
            print(f"✅ Set Redis key 'environment_monitor': {message}")

        else:
            print("⚠️ Unknown device, both slots full. Ignoring.")

    except socket.timeout:
        pass  # không có gì nhận


    time.sleep(0.2)