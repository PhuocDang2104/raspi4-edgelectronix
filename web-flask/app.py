import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import socket
import redis
import json

# 🚀 Flask + SocketIO setup
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'admin'
socketio = SocketIO(app, cors_allowed_origins="*")

# 🧠 Redis pub/sub setup
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)

# 👂 Redis listener task – chạy song song
def redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('dashboard_updates')

    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                payload = json.loads(message['data'])
                print("📡 Redis received")

                # Gửi dữ liệu perfumes khi có cập nhật
                if 'update_perfume_catalog' in payload:
                    socketio.emit('update_perfume_catalog', payload['update_perfume_catalog'])

                # (Tuỳ chọn) Nếu sau này muốn dùng lại update_shelf_stock hoặc update_kpi
                # if 'update_shelf_stock' in payload:
                #     socketio.emit('update_shelf_stock', payload['update_shelf_stock'])

                # if 'update_kpi' in payload:
                #     socketio.emit('update_kpi', payload['update_kpi'])

            except Exception as e:
                print(f"❌ Redis listener error: {e}")

# 🌐 Routes
@app.route('/')
def home():
    return render_template('smartlcd.html')

# 🔌 Socket.IO connection event
@socketio.on('connect')
def on_connect():
    print("✅ Client connected!")

# 🧠 Main app entry
if __name__ == '__main__':
    socketio.start_background_task(target=redis_listener)

    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    local_ip = get_local_ip()
    print(f"🚀 Server running at:")
    print(f"→ http://localhost:5000")
    print(f"→ http://{local_ip}:5000")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
