import redis
import time

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# TTL (giây) cho suggest id trước khi hết hiệu lực
SUGGEST_TTL = 20

def main():
    print("🚀 Perfume Matcher started.")
    last_suggest = None
    last_suggest_time = 0

    while True:
        try:
            # lấy perfume id được AI suggest
            suggest_id = redis_client.get("uart_model_result")
            if suggest_id and suggest_id != last_suggest:
                last_suggest = suggest_id
                last_suggest_time = time.time()
                print(f"💡 New suggested perfume: {last_suggest}")

            # lấy perfume id thực tế được pick
            picked_id = redis_client.get("selected_perfume_id_from_udp")
            if picked_id:
                print(f"📦 Picked perfume: {picked_id}")

                # so khớp với suggest
                if (
                    last_suggest
                    and picked_id == last_suggest
                    and (time.time() - last_suggest_time) <= SUGGEST_TTL
                ):
                    print(f"🎯 MATCH! Picked {picked_id} == Suggested {last_suggest}")

                    # đặt flag cho app.py biết để show rating UI
                    redis_client.set("trigger_rating_request", picked_id, ex=10)

                    # reset để tránh lặp lại
                    last_suggest = None
                    last_suggest_time = 0

            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            break
        except Exception as e:
            print("⚠️ Error in matcher loop:", e)
            time.sleep(1)

if __name__ == "__main__":
    main()
