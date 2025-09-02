import redis
import socket
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def ensure_hash_key(key: str):
    """Đảm bảo key là hash. Nếu key tồn tại nhưng khác kiểu → rename làm backup."""
    t = redis_client.type(key)  # 'none' | 'string' | 'hash' | ...
    if t != 'hash' and t != 'none':
        backup = f"{key}:backup:{int(time.time())}"
        try:
            redis_client.rename(key, backup)
            print(f"ℹ️ Redis key '{key}' không phải hash (kiểu: {t}). Đã đổi tên thành '{backup}'.")
        except redis.exceptions.ResponseError:
            # nếu không rename được thì xoá
            redis_client.delete(key)
            print(f"ℹ️ Không rename được '{key}'. Đã xoá để tạo lại dưới dạng hash.")

# Đảm bảo loại key ngay từ đầu
ensure_hash_key('environment_monitor')

UDP_IP = "::"
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.5)

print("📡 Listening on UDP port", UDP_PORT)

# IPv6 cố định của 2 thiết bị
addr1_ip = "fd85:946:886f:1:929b:58ff:9dc2:7768"
addr2_ip = "fdf3:907:f99e:9fa1:17d8:992d:fecc:6346"

while True:
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode(errors="ignore").strip()
        sender_ip = addr[0]

        # Thiết bị 1 (perfume selector)
        if sender_ip == addr1_ip:
            redis_client.set('selected_perfume_id_from_udp', message)
            print(f"* [Perfume] Set 'selected_perfume_id_from_udp': {message}")

        # Thiết bị 2 (Env + Drop)
        elif sender_ip == addr2_ip:
            if message.lower() == "drop":
                redis_client.set('drop_detect_event', "1")
                print(f"-- [Drop] Phát hiện đỗ vỡ AI event")

            elif message.startswith("Temp"):
                try:
                    # Format: "Temp=26.02C,Hum=57.4%"
                    parts = message.split(",")
                    temp_str = parts[0].replace("Temp=", "").replace("C", "")
                    hum_str  = parts[1].replace("Hum=", "").replace("%", "")

                    temperature = float(temp_str)
                    humidity    = float(hum_str)

                    try:
                        redis_client.hset('environment_monitor', mapping={
                            'temperature': temperature,
                            'humidity': humidity
                        })
                    except redis.exceptions.ResponseError as e:
                        # Nếu key đang sai kiểu → sửa lại & thử lần 2
                        if "WRONGTYPE" in str(e).upper():
                            ensure_hash_key('environment_monitor')
                            redis_client.hset('environment_monitor', mapping={
                                'temperature': temperature,
                                'humidity': humidity
                            })
                        else:
                            raise

                    print(f"-- [Env] Nhiệt độ: {temperature}°C | Độ ẩm: {humidity}%")

                except Exception as e:
                    print(f"⚠️ Lỗi parse message '{message}': {e}")

            else:
                print(f"⚠️ [Device2] Unknown message format: {message}")

        else:
            # Không khớp 2 IP đã cấu hình
            print(f"⚠️ Unknown device {sender_ip}, ignoring.")

    except socket.timeout:
        pass

    time.sleep(0.2)
