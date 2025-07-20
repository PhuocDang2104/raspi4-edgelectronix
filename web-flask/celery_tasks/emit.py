### Updated emit.py with filtering by selected perfume_id

import psycopg2
import time
import json
import redis

# PostgreSQL config
POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'admin'
}

# Redis config
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Selected perfume ID (can be dynamically updated later)
SELECTED_ID = 'P005'

def run_emit_loop():
    previous_state = {}
    while True:
        try:
            with psycopg2.connect(**POSTGRES_CONFIG) as conn:
                with conn.cursor() as cur:
                    # Query only the selected perfume_id
                    cur.execute("""
                        SELECT perfume_id, title, subtitle, description, star, review, volume, price,
                               longevity, sillage, projection, occasion_1, occasion_2, occasion_3,
                               note_1, note_2, note_3, note_4, note_5
                        FROM perfumes
                        WHERE perfume_id = %s
                    """, (SELECTED_ID,))

                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    data = [dict(zip(columns, row)) for row in rows]

            # Publish to Redis
            redis_client.publish('dashboard_updates', json.dumps({
                'update_perfume_catalog': data
            }))

            print(f"✅ Published selected perfume {SELECTED_ID} to Redis → dashboard_updates")

        except Exception as e:
            print(f"❌ Emit error: {e}")

        time.sleep(1)

if __name__ == '__main__':
    run_emit_loop()
