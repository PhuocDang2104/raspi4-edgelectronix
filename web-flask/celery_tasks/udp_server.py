import redis
import socket
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

UDP_IP = "::"
UDP_PORT = 12345

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("📡 Listening on UDP port", UDP_PORT)

# Gán sẵn IPv6
addr1_ip = "fd85:946:886f:1:985a:373:6248:3d88"
addr2_ip = "fd85:946:886f:1:b215:9820:4136:571d"

while True:
    sock.settimeout(0.5)
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        print("Received from", addr, ":", message)

        if addr1_ip is None or addr[0] == addr1_ip:
            addr1_ip = addr[0]
            redis_client.set('selected_perfume_id_from_udp', message)
            print(f"✅ Set Redis key 'selected_perfume_id_from_udp': {message}")

        elif addr2_ip is None or addr[0] == addr2_ip:
            addr2_ip = addr[0]
            redis_client.set('environment_monitor', message)
            print(f"✅ Set Redis key 'environment_monitor': {message}")

        else:
            print("⚠️ Unknown device, both slots full. Ignoring.")

    except socket.timeout:
        pass

    time.sleep(0.2)