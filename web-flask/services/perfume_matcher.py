import redis
import time

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# TTL (giây) cho suggest id trước khi hết hiệu lực
SUGGEST_TTL = 10 # 10 giây

def main():
    print("🚀 Perfume Matcher started.")
    last_suggest = None
    last_suggest_time = 0

    while True:
        try:
            # lấy perfume id được AI suggest
            raw_suggest = redis_client.get("uart_model_result")
            suggest_id = raw_suggest.strip() if raw_suggest else None

            # nếu có suggest mới khác với last_suggest -> cập nhật
            if suggest_id:
                if suggest_id != last_suggest:
                    last_suggest = suggest_id
                    last_suggest_time = time.time()
                    print(f"💡 New suggested perfume: {last_suggest} (at {time.strftime('%H:%M:%S')})")
            else:
                # không có suggest trong redis: nếu last_suggest quá cũ thì clear
                if last_suggest and (time.time() - last_suggest_time) > SUGGEST_TTL:
                    print(f"⏳ Suggest {last_suggest} expired, clearing cache")
                    last_suggest = None
                    last_suggest_time = 0

            # lấy perfume id thực tế được pick
            raw_picked = redis_client.get("selected_perfume_id_from_udp")
            picked_id = raw_picked.strip() if raw_picked else None

            if picked_id:
                print(f"📦 Picked perfume: {picked_id}")

                # nếu đã có trigger đang tồn tại, bỏ qua (để tránh re-trigger)
                if redis_client.exists("trigger_rating_request"):
                    print("⚠️ trigger_rating_request already exists in Redis — skipping re-trigger.")
                else:
                    # so khớp với suggest
                    if (
                        last_suggest
                        and picked_id == last_suggest
                        and (time.time() - last_suggest_time) <= SUGGEST_TTL
                    ):
                        print(f"🎯 MATCH! Picked {picked_id} == Suggested {last_suggest}")

                        # đặt flag cho app.py biết để show rating UI (với TTL)
                        redis_client.set("trigger_rating_request", picked_id, ex=10)

                        # XÓA các key nguồn để tránh reprocessing liên tục
                        deleted = redis_client.delete("uart_model_result", "selected_perfume_id_from_udp")
                        print(f"🧹 Cleared source keys (deleted {deleted} keys).")

                        # reset cache nội bộ để đảm bảo không re-trigger
                        last_suggest = None
                        last_suggest_time = 0

            # giảm rate một chút
            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            break
        except Exception as e:
            print("⚠️ Error in matcher loop:", e)
            time.sleep(1)

if __name__ == "__main__":
    main()
