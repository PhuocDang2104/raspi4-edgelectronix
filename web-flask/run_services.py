import subprocess
import os

def run_raspi():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Các file ở root
    root_scripts = ["app.py", "run_emit.py"]

    # Các file trong /services
    service_scripts = [
        "mqtt_ai_confidence.py",
        "mqtt_ratings.py",
        "mqtt_shelf_data.py",
        "mqtt.py",
        "perfume_matcher.py",
        "uart_xg24.py",
        "udp_server.py",
    ]

    processes = []

    # Chạy file ở root
    for script in root_scripts:
        filepath = os.path.join(base_dir, script)
        print(f"🔹 Starting {filepath} ...")
        p = subprocess.Popen(["python", filepath])
        processes.append(p)

    # Chạy file trong /services
    services_dir = os.path.join(base_dir, "services")
    for script in service_scripts:
        filepath = os.path.join(services_dir, script)
        print(f"🔹 Starting {filepath} ...")
        p = subprocess.Popen(["python", filepath])
        processes.append(p)

    # Chờ tất cả process (nếu muốn script này giữ cho đến khi stop)
    for p in processes:
        p.wait()

if __name__ == "__main__":
    run_raspi()
