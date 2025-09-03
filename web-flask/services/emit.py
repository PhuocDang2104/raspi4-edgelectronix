# emit.py — publish both update_perfume_catalog (existing) and update_perfume_xg24_result (from UART -> perfumes_6col)
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

# Selected perfume ID (UI selector / UDP key)
SELECTED_ID = 'P005'

def listen_perfume_selector():
    """Optional background listener for UI selector channel."""
    global SELECTED_ID
    pubsub = redis_client.pubsub()
    pubsub.subscribe('perfume_selector_channel')
    print("📡 Listening for perfume_id selection on 'perfume_selector_channel' ...")
    for msg in pubsub.listen():
        if msg['type'] == 'message':
            try:
                new_id = msg['data'].decode().strip()
                print(f"🆕 Received new SELECTED_ID from channel: {new_id}")
                SELECTED_ID = new_id
            except Exception as e:
                print("Error decoding selector msg:", e)

threading.Thread(target=listen_perfume_selector, daemon=True).start()

def run_emit_loop():
    global SELECTED_ID
    last_sent_id = None
    last_sent_data = None

    # For XG/uart path (perfumes_6col)
    last_sent_uart_id = None
    last_sent_uart_data = None

    # For suggestions (top2/top3 brief titles)
    last_sent_suggestions = None  # store list of dicts for comparison

    while True:
        try:
            # ---------------------------
            # 1) Keep SELECTED_ID in sync (UDP/other key)
            # ---------------------------
            udp_selected_id = redis_client.get('selected_perfume_id_from_udp')
            if udp_selected_id:
                try:
                    udp_selected_id = udp_selected_id.decode().strip()
                except:
                    pass
                if udp_selected_id and udp_selected_id != SELECTED_ID:
                    print(f"🔄 SELECTED_ID updated from Redis key selected_perfume_id_from_udp: {udp_selected_id}")
                    SELECTED_ID = udp_selected_id

            # ---------------------------
            # 2) Existing lookup on table `perfumes` for SELECTED_ID
            # ---------------------------
            with psycopg2.connect(**POSTGRES_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT perfume_id, title, subtitle, description, star, review, volume, price,
                               longevity, sillage, projection, occasion_1, occasion_2, occasion_3,
                               note_1, note_2, note_3, note_4, note_5, country, brand, year
                        FROM perfumes
                        WHERE perfume_id = %s
                    """, (SELECTED_ID,))
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description] if rows else []
                    data = [dict(zip(columns, row)) for row in rows] if rows else []

            if SELECTED_ID != last_sent_id or data != last_sent_data:
                redis_client.publish('dashboard_updates', json.dumps({
                    'update_perfume_catalog': data
                }))
                print(f"✅ Published new perfume {SELECTED_ID} to Redis → dashboard_updates (update_perfume_catalog)")
                last_sent_id = SELECTED_ID
                last_sent_data = data

            # ---------------------------
            # 3) UART-driven path: check uart_model_result key and lookup perfumes_6col
            # ---------------------------
            uart_val = redis_client.get('uart_model_result')

            
            if uart_val:
                try:
                    uart_id = uart_val.decode().strip()
                except:
                    uart_id = uart_val if isinstance(uart_val, str) else None

                if uart_id:
                    # Query perfumes_6col for this uart_id
                    with psycopg2.connect(**POSTGRES_CONFIG) as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                SELECT perfume_id, title, subtitle, longevity, sillage, projection
                                FROM perfumes_6col
                                WHERE perfume_id = %s
                            """, (uart_id,))
                            rows_x = cur.fetchall()
                            cols_x = [desc[0] for desc in cur.description] if rows_x else []
                            data_x = [dict(zip(cols_x, r)) for r in rows_x] if rows_x else []

                    # Publish if new/different
                    if uart_id != last_sent_uart_id or data_x != last_sent_uart_data:
                        redis_client.publish('xg24_result', json.dumps({
                            'update_perfume_xg24_result': data_x
                        }))
                        print(f"📦 UART lookup result for {uart_id}: {data_x}")
                        print(f"🔔 Published UART lookup {uart_id} → dashboard_updates (update_perfume_xg24_result), rows={len(data_x)}")
                        last_sent_uart_id = uart_id
                        last_sent_uart_data = data_x
                    else:
                        # no change -> do nothing
                        pass
                        
                        # ---------------------------
                        # 4) Fetch top2 & top3 brief titles and publish separately
                        # ---------------------------
                        try:
                            # read top2 / top3 from redis keys set by uart reader
                            raw2 = redis_client.get('uart_model_result_2')
                            raw3 = redis_client.get('uart_model_result_3')
                            id2 = None
                            id3 = None
                            if raw2:
                                try:
                                    id2 = raw2.decode().strip()
                                except:
                                    id2 = raw2 if isinstance(raw2, str) else None
                            if raw3:
                                try:
                                    id3 = raw3.decode().strip()
                                except:
                                    id3 = raw3 if isinstance(raw3, str) else None

                            suggestions = []
                            # query brief info for each (preserve order 2 then 3)
                            for cand_id in (id2, id3):
                                if not cand_id:
                                    continue
                                try:
                                    with psycopg2.connect(**POSTGRES_CONFIG) as conn:
                                        with conn.cursor() as cur:
                                            cur.execute("""
                                                SELECT perfume_id, title
                                                FROM perfumes_6col
                                                WHERE perfume_id = %s
                                            """, (cand_id,))
                                            row = cur.fetchone()
                                            if row:
                                                suggestions.append({
                                                    'perfume_id': row[0],
                                                    'title': row[1]
                                                })
                                except Exception as e:
                                    print(f"❌ Error querying brief title for {cand_id}: {e}")
                                    # continue to next

                            # Publish suggestions if changed (or if previously None -> first time)
                            if suggestions != last_sent_suggestions:
                                # publish under a separate key inside the same 'dashboard_updates' channel
                                redis_client.publish('dashboard_updates', json.dumps({
                                    'update_perfume_suggestions': suggestions
                                }))
                                print(f"🔎 Published suggestions (top2/top3) → dashboard_updates (update_perfume_suggestions): {suggestions}")
                                last_sent_suggestions = suggestions

                        except Exception as e:
                            print("❌ Error building/publishing suggestions:", e)

                    # Optional: clear uart key to mark consumed (uncomment if desired)
                    # redis_client.delete('uart_model_result')

                    # Optional: clear uart key to mark consumed (uncomment if desired)
                    # redis_client.delete('uart_model_result')

        except Exception as e:
            print(f"❌ Emit error: {e}")

        # small sleep to avoid busy-loop
        time.sleep(0.9)

if __name__ == '__main__':
    run_emit_loop()
