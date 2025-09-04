#!/usr/bin/env python3
"""
perfume_gui_sender.py

Giao diện đơn giản để chọn perfume ID và gửi vào Redis key:
    selected_perfume_id_from_udp
"""
import tkinter as tk
from tkinter import ttk, messagebox
import time
import redis

PERFUME_IDS = [
    "P001", "P005", "P007", "P017", "P020",
    "P026", "P030", "P045", "P047", "P049"
]

REDIS_KEY = "selected_perfume_id_from_udp"


class PerfumeSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fake Perfume Sender")
        self.root.resizable(False, False)

        main = ttk.Frame(root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")

        # Redis connection frame
        conn_frame = ttk.LabelFrame(main, text="Redis connection", padding=8)
        conn_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="w")
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(conn_frame, textvariable=self.host_var, width=14).grid(row=0, column=1, sticky="w", padx=4)

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(8,0))
        self.port_var = tk.StringVar(value="6379")
        ttk.Entry(conn_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, sticky="w", padx=4)

        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_redis)
        self.connect_btn.grid(row=0, column=4, padx=(8,0))

        # Selection frame
        sel_frame = ttk.LabelFrame(main, text="Chọn Perfume ID", padding=8)
        sel_frame.grid(row=1, column=0, pady=(10,0), sticky="ew")

        ttk.Label(sel_frame, text="Perfume ID:").grid(row=0, column=0, sticky="w")
        self.selected_var = tk.StringVar(value=PERFUME_IDS[0])
        self.combo = ttk.Combobox(sel_frame, textvariable=self.selected_var, values=PERFUME_IDS, state="readonly", width=12)
        self.combo.grid(row=0, column=1, padx=8, sticky="w")

        self.send_btn = ttk.Button(sel_frame, text="Send to Redis", command=self.send_selected, state="disabled")
        self.send_btn.grid(row=0, column=2, padx=(10,0))

        # Log frame
        log_frame = ttk.LabelFrame(main, text="Log", padding=8)
        log_frame.grid(row=2, column=0, pady=(10,0), sticky="nsew")

        self.log_text = tk.Text(log_frame, height=8, width=55, state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        # Status bar
        self.status_var = tk.StringVar(value="Not connected to Redis")
        status = ttk.Label(main, textvariable=self.status_var, relief="sunken", anchor="w")
        status.grid(row=3, column=0, pady=(8,0), sticky="ew")

        # Internal
        self.redis_client = None

        # Bind Enter key to send
        self.root.bind("<Return>", lambda e: self.send_selected())

    def connect_redis(self):
        host = self.host_var.get().strip()
        port_s = self.port_var.get().strip()
        try:
            port = int(port_s)
        except ValueError:
            messagebox.showerror("Error", "Port không hợp lệ")
            return

        try:
            r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
            r.ping()
            self.redis_client = r
            self.log(f"✔️ Connected to Redis {host}:{port}")
            self.status_var.set(f"Connected: {host}:{port}")
            self.send_btn.config(state="normal")
            self.connect_btn.config(text="Reconnect")
        except Exception as e:
            self.redis_client = None
            self.status_var.set("Not connected to Redis")
            self.send_btn.config(state="disabled")
            messagebox.showerror("Redis connection failed", str(e))
            self.log(f"❌ Redis connect failed: {e}")

    def send_selected(self):
        pid = self.selected_var.get().strip()
        if not pid:
            messagebox.showwarning("No selection", "Vui lòng chọn một Perfume ID")
            return
        if self.redis_client is None:
            messagebox.showwarning("Not connected", "Chưa kết nối tới Redis. Nhấn Connect trước.")
            return
        try:
            self.redis_client.set(REDIS_KEY, pid)
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            self.log(f"{ts} → Sent {pid} to '{REDIS_KEY}'")
        except Exception as e:
            self.log(f"❌ Error while setting Redis key: {e}")
            messagebox.showerror("Error", f"Không thể gửi tới Redis:\n{e}")

    def log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")


if __name__ == "__main__":
    try:
        import tkinter as tk  # confirm tkinter available
    except Exception:
        print("tkinter không sẵn có trên hệ thống. Cài hoặc bật tkinter để chạy GUI.")
        raise

    root = tk.Tk()
    style = ttk.Style(root)
    # Optional: use default theme, keep simple
    app = PerfumeSenderApp(root)
    root.mainloop()