# PID_sim_console.py
import redis
import time

PERFUME_IDS = [
    "P001", "P005", "P007", "P017", "P020",
    "P026", "P030", "P045", "P047", "P049"
]
REDIS_KEY = "selected_perfume_id_from_udp"

def connect_redis():
    return redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def send_pid(r, pid):
    r.set(REDIS_KEY, pid)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] ✔ Sent {pid} -> {REDIS_KEY}")

def menu():
    r = connect_redis()
    print("=== Perfume ID Simulator (Console) ===")
    while True:
        for i, pid in enumerate(PERFUME_IDS, start=1):
            print(f"{i:2}. {pid}")
        print(" 0. Thoát")
        choice = input("Chọn số để gửi: ").strip()
        if choice == "0":
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(PERFUME_IDS):
                send_pid(r, PERFUME_IDS[idx])
            else:
                print("❌ Lựa chọn không hợp lệ.")
        except ValueError:
            print("❌ Vui lòng nhập số.")

if __name__ == "__main__":
    menu()