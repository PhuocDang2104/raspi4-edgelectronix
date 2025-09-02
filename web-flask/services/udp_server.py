import redis
import socket
import time

# Kết nối Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# UDP socket IPv6
UDP_IP = "::"   # Lắng nghe tất cả IPv6
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("📡 Listening on UDP port", UDP_PORT)

# Địa chỉ IPv6 cố định cho 2 device
addr1_ip = "fdf3:907:f99e:9fa1:e09a:2d59:dd67:b31"    # Perfume selector
addr2_ip = "fdf3:907:f99e:9fa1:17d8:992d:fecc:6346"   # Env + drop sensor

while True:
    sock.settimeout(0.5)
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        sender_ip = addr[0]

        # ----------------
        # Device 1 (Perfume)
        # ----------------
        if sender_ip == addr1_ip:
            redis_client.set('selected_perfume_id_from_udp', message)
            print(f"* [Perfume] Set Redis key 'selected_perfume_id_from_udp': {message}")

        # ----------------
        # Device 2 (Env + Drop)
        # ----------------
        elif sender_ip == addr2_ip:
            if message.lower() == "drop":
                redis_client.set('drop_detect_event', "1")
                print(f"-- [Drop] Phát hiện đỗ vỡ AI event")

            elif message.startswith("Temp"):
                try:
                    # Format: "Temp=28.5C,Hum=65%"
                    parts = message.split(",")
                    temp_str = parts[0].replace("Temp=", "").replace("C", "")
                    hum_str = parts[1].replace("Hum=", "").replace("%", "")

                    temperature = float(temp_str)
                    humidity = float(hum_str)

                    # Lưu vào Redis dạng hash
                    redis_client.hset('environment_monitor', mapping={
                        'temperature': temperature,
                        'humidity': humidity
                    })
                    print(f"-- [Env] Nhiệt độ: {temperature}°C | Độ ẩm: {humidity}%")

                except Exception as e:
                    print(f"Lỗi parse message '{message}': {e}")

            else:
                print(f"⚠️ [Device2] Unknown message format: {message}")

        else:
            print(f"⚠️ Unknown device {sender_ip}, ignoring.")

    except socket.timeout:
        pass

    time.sleep(0.2)
