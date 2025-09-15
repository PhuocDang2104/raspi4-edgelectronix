import eventlet
eventlet.monkey_patch()

from ai_models.ner_normalize import normalize_entity, ner_normalize
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import socket
import redis
import json
import spacy

def build_request_json(doc):
    # build initial raw request from entities (same as before)
    request = {
        "gender": "Any",
        "brand": "Any",
        "notes": [],
        "preferred_accord": [],
        "sillage": "Any",
        "longevity": "Any",
        "price": "Any",
    }

    for ent in doc.ents:
        raw_text = ent.text
        label = ent.label_
        normalized = normalize_entity(label, raw_text)

        if not normalized:
            continue

        if label == "GENDER" and "gender" in normalized:
            request["gender"] = normalized["gender"]

        elif label == "BRAND" and "brand" in normalized:
            request["brand"] = normalized["brand"]

        elif label == "PREFERRED_ACCORD":
            if "note" in normalized:
                request["notes"].append(normalized["note"])
            if "accord" in normalized:
                request["preferred_accord"].append(normalized["accord"])

        elif label == "SILLAGE" and "sillage" in normalized:
            request["sillage"] = normalized["sillage"]

        elif label == "LONGEVITY" and "longevity" in normalized:
            request["longevity"] = normalized["longevity"]

        elif label == "PRICE" and "price" in normalized:
            request["price"] = normalized["price"]

        elif label == "AGE" and "age" in normalized:
            # chưa dùng, bỏ qua
            pass

    # loại trùng (keep order optional)
    request["notes"] = list(dict.fromkeys(request["notes"]))
    request["preferred_accord"] = list(dict.fromkeys(request["preferred_accord"]))

    # --- CRITICAL: call ner_normalize to apply full normalization and accord->notes expansion ---
    # ner_normalize returns: gender, brand, notes_canonical, accords_canonical, sillage, longevity, price
    try:
        gender, brand, notes_canonical, accords_canonical, sillage, longevity, price = ner_normalize(
            {
                "gender": request.get("gender", "Any"),
                "brand": request.get("brand", "Any"),
                "notes": request.get("notes", []),
                "preferred_accord": request.get("preferred_accord", []),
                "sillage": request.get("sillage", "Any"),
                "longevity": request.get("longevity", "Any"),
                "price": request.get("price", "Any"),
                # optionally include raw text for detection:
                # "text": doc.text
            }
        )
        # update request using normalized results
        request["gender"] = gender
        request["brand"] = brand
        request["notes"] = notes_canonical
        request["preferred_accord"] = accords_canonical
        request["sillage"] = sillage
        request["longevity"] = longevity
        request["price"] = price
    except Exception as e:
        # fallback: if ner_normalize fails, keep original request
        print(f"❌ ner_normalize error: {e}")

    return request

# Load model 1 lần khi server khởi động
nlp_model = spacy.load("ai_models/output/model-last")

#  Flask + SocketIO setup
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'admin'
socketio = SocketIO(app, cors_allowed_origins="*")

#  Redis pub/sub setup
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)

#  Redis listener task – chạy song song
def redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('dashboard_updates', 'xg24_result')

    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                payload = json.loads(message['data'])
                print("📡 Redis received")

                # Gửi dữ liệu perfumes khi có cập nhật
                if 'update_perfume_catalog' in payload:
                    socketio.emit('update_perfume_catalog', payload['update_perfume_catalog'])

                # Bắt thêm luồng XG24 result
                if 'update_perfume_xg24_result' in payload:
                    socketio.emit('update_perfume_xg24_result', payload['update_perfume_xg24_result'])
                    print(f"📦 Forwarded XG24 result → socketio: {payload['update_perfume_xg24_result']}")

                # Gửi brief suggestions (top2/top3) — mới thêm
                if 'update_perfume_suggestions' in payload:
                    socketio.emit('update_perfume_suggestions', payload['update_perfume_suggestions'])
                    print(f"➡ Emitted socketio: update_perfume_suggestions ({payload['update_perfume_suggestions']})")


            except Exception as e:
                print(f"❌ Redis listener error: {e}")

def watch_trigger():
    while True:
        perfume_id = redis_client.get("trigger_rating_request")
        if perfume_id:
            perfume_id = perfume_id.decode()
            print(f"⭐ Trigger rating UI for perfume {perfume_id}")
            socketio.emit("show_rating_request", {"perfume_id": perfume_id})
            redis_client.delete("trigger_rating_request")  # xoá để không lặp

# 🌐 Routes
@app.route('/')
def home():
    return render_template('smartlcd.html')

# 🔌 Socket.IO connection event
@socketio.on('connect')
def on_connect():
    print("✅ Client connected!")

@socketio.on('ai_request')
def handle_ai_request(data):
    if 'form_input' in data:
        form_input = data['form_input']
        udp_message = json.dumps(form_input)
        redis_client.set("uart_outgoing_message", udp_message)
        print("- Received Manual Form Input:")
        for key, value in form_input.items():
            print(f"{key}: {value}")
    elif 'NLP_input' in data:
        NLP_input = data['NLP_input']
        print(f"- Received NLP Input: {NLP_input}")

        # Run inference
        doc = nlp_model(NLP_input)

        # Gom JSON chuẩn
        results = build_request_json(doc)

        print("=== NLP normalized JSON ===")
        for k, v in results.items():
            print(f"{k}: {v}")

        try:
            uart_message = json.dumps(results)
            redis_client.set("uart_outgoing_message", uart_message)
            print(f"✅ Queued message for EFR32 via Redis: {uart_message}")
        except Exception as e:
            print(f"❌ Failed to queue message for UDP: {e}")

        #  Gửi lên frontend qua Socket.IO
        socketio.emit('ai_response', results)
    else:
        print("No recognizable data received.")
        


@socketio.on("submit_rating")
def handle_rating(data):
    perfume_id = data.get("perfume_id")
    product_rating = data.get("product_rating")
    ai_rating = data.get("ai_rating")

    if not perfume_id or not product_rating or not ai_rating:
        return

    entry = {
        "perfume_id": perfume_id,
        "product_rating": product_rating,
        "ai_rating": ai_rating
    }
    redis_client.rpush("ratings", json.dumps(entry))

    print(f"[⭐] Rating received → {entry}")


# Main app entry
if __name__ == '__main__':
    socketio.start_background_task(target=redis_listener)
    socketio.start_background_task(target=watch_trigger)

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
