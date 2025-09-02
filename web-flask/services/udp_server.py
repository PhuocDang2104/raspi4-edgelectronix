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
addr1_ip = "fdf3:907:f99e:9fa1:e09a:2d59:dd67:b31"
addr2_ip = "fdf3:907:f99e:9fa1:17d8:992d:fecc:6346"

while True:
    sock.settimeout(0.5)
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        
        

        if addr1_ip is None or addr[0] == addr1_ip:
            addr1_ip = addr[0]
            redis_client.set('selected_perfume_id_from_udp', message)
            print(f"* Set Redis key 'selected_perfume_id_from_udp': {message}")

        elif addr2_ip is None or addr[0] == addr2_ip:
            addr2_ip = addr[0]
            if message.upper().startswith("TEMP:"):
                try:
                    parts = message.split(",")
                    temp_str = parts[0].replace("Temp=", "").replace("C", "")
                    hum_str = parts[1].replace("Hum=", "").replace("%", "")
                    
                    # Chuyển sang float
                    temperature = float(temp_str)
                    humidity = float(hum_str)
                    # Lưu vào Redis
                    redis_client.hset('environment_monitor', mapping={
                        'temperature': temperature,
                        'humidity': humidity
                    })

                    print(f"-- Nhiệt độ: {temperature}°C | Độ ẩm: {humidity}%")
                    
                except Exception as e:
                    print(f"Lỗi parse message '{message}': {e}")
                    
            elif message.lower() == "drop":
                redis_client.set('drop_detect_event', "1")
                print(f"-- Phát hiện đỗ vỡ AI event: {message}")

        else:
            print("⚠️ Unknown device, both slots full. Ignoring.")

    except socket.timeout:
        pass

    time.sleep(0.2)