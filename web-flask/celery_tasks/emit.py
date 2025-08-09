### Updated emit.py with filtering by selected perfume_id

import psycopg2
import time
import json
import redis
import threading

# PostgreSQL config
POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'admin'
}

# Redis config
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Selected perfume ID 
SELECTED_ID = 'P005'

def listen_perfume_selector():
    global SELECTED_ID
    pubsub = redis_client.pubsub()
    pubsub.subscribe('perfume_selector_channel')
    print("📡 Listening for perfume_id selection...")

    for msg in pubsub.listen():
        if msg['type'] == 'message':
            new_id = msg['data'].decode()
            print(f"🆕 Received new SELECTED_ID: {new_id}")
            SELECTED_ID = new_id

# Start pubsub listener in background thread
threading.Thread(target=listen_perfume_selector, daemon=True).start()

def run_emit_loop():
    global SELECTED_ID
    last_sent_id = None
    last_sent_data = None

    while True:
        try:
            # 🔁 Cập nhật SELECTED_ID nếu Redis key có thay đổi
            udp_selected_id = redis_client.get('selected_perfume_id_from_udp')
            if udp_selected_id:
                udp_selected_id = udp_selected_id.decode()
                if udp_selected_id != SELECTED_ID:
                    print(f"🔄 SELECTED_ID updated from Redis key: {udp_selected_id}")
                    SELECTED_ID = udp_selected_id

            with psycopg2.connect(**POSTGRES_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT perfume_id, title, subtitle, description, star, review, volume, price,
                                longevity, sillage, projection, occasion_1, occasion_2, occasion_3,
                                note_1, note_2, note_3, note_4, note_5, country, brand 
                        FROM perfumes
                        WHERE perfume_id = %s
                    """, (SELECTED_ID,))
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    data = [dict(zip(columns, row)) for row in rows]

            # 📌 Kiểm tra xem dữ liệu có thay đổi không
            if SELECTED_ID != last_sent_id or data != last_sent_data:
                redis_client.publish('dashboard_updates', json.dumps({
                    'update_perfume_catalog': data
                }))
                print(f"✅ Published new perfume {SELECTED_ID} to Redis → dashboard_updates")
                last_sent_id = SELECTED_ID
                last_sent_data = data
            else:
                # Không in spam nữa
                pass

        except Exception as e:
            print(f"❌ Emit error: {e}")

        time.sleep(1)

if __name__ == '__main__':
    run_emit_loop()
