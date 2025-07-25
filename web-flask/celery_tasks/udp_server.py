import redis
import socket

redis_client = redis.Redis(host='localhost', port=6379, db=0)

UDP_IP = "::"
UDP_PORT = 12345

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("📡 Listening on UDP port", UDP_PORT)
while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode().strip()
    print("📨 Received from", addr, ":", message)

    # 👉 Ghi nội dung vào key riêng
    redis_client.set('selected_perfume_id_from_udp', message)
    print(f"🔁 Set SELECTED_ID via Redis key: {message}")