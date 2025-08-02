import redis
import socket
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

UDP_IP = "::"
UDP_PORT = 12345

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("📡 Listening on UDP port", UDP_PORT)

# Lưu địa chỉ EFR32 để có thể gửi ngược lại
last_sender_addr = None

while True:
    # ✅ 1. Check nếu có dữ liệu gửi từ EFR32
    sock.settimeout(0.5)  # không block vĩnh viễn
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        print("📨 Received from", addr, ":", message)

        # Lưu địa chỉ gửi để còn gửi ngược lại
        last_sender_addr = addr

        # Ghi Redis key để frontend/web đọc
        redis_client.set('selected_perfume_id_from_udp', message)
        print(f"✅ Set Redis key 'selected_perfume_id_from_udp': {message}")

    except socket.timeout:
        pass  # không có gì nhận

    # ✅ 2. Check có message từ Redis để gửi ngược lại không
    message2 = redis_client.get("udp_outgoing_message")
    if message2 and last_sender_addr:
        try:
            message2 = message2.decode().strip()
            print(f"📨 Got message from Redis: {message2}")

            # Gửi lại cho EFR32
            sock.sendto(message2.encode(), last_sender_addr)
            print(f"📤 Sent to {last_sender_addr}")

            # Xoá key sau khi gửi
            redis_client.delete("udp_outgoing_message")

        except Exception as e:
            print(f"❌ Error sending UDP: {e}")

    time.sleep(0.2)