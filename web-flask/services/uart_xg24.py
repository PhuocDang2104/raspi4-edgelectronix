#!/usr/bin/env python3
"""
uart_redis_csv_sender.py
- Terminal UART interactive (gõ gửi)
- Background thread: poll Redis key 'uart_outgoing_message' (contains JSON bytes),
  convert to PREF CSV line (same format as gen_csv in your GUI) and send via UART.
- Bổ sung: nếu perfume ID trùng với các ID chỉ định thì kích sáng LED trên GPIO tương ứng
"""

import serial
import threading
import redis
import json
import time
import sys
import traceback
import re

# -------------------------
# Vocabularies (same as GUI)
# -------------------------
GENDER_NAMES    = ["men", "unisex", "women"]
BRAND_NAMES     = [
    "antonio-puig",
    "avon",
    "balenciaga",
    "bdk-parfums",
    "beverly-hills-polo-club",
    "burberry",
    "by-kilian",
    "carolina-herrera",
    "cerruti",
    "coty",
    "escada",
    "fragonard",
    "frederic-malle",
    "givenchy",
    "goldfield-banks-australia",
    "gucci",
    "guerlain",
    "hugo-boss",
    "issey-miyake",
    "jean-paul-gaultier",
    "juicy-couture",
    "kenneth-cole",
    "lalique",
    "lancome",
    "lanvin",
    "lorenzo-villoresi",
    "mugler",
    "narciso-rodriguez",
    "natura",
    "oriflame",
    "paco-rabanne",
    "salvatore-ferragamo",
    "the-body-shop",
    "trussardi",
    "vilhelm-parfumerie",
    "xerjoff",
    "yves-saint-laurent",
    "zadig-voltaire",
    "zara",
    "zoologist-perfumes"
]
SILLAGE_NAMES   = ["heavy", "high", "moderate", "soft"]
LONGEVITY_NAMES = ["light", "moderate", "strong", "very strong"]
PRICE_NAMES     = ["affordable", "average", "high-end"]
ACCORD_NAMES    = [
    "aldehydic","amber","animalic","aquatic","aromatic","balsamic","beeswax","cannabis",
    "cherry","chocolate","citrus","coconut","coffee","earthy","floral","fresh",
    "fresh spicy","fruity","green","herbal","honey","iris","lactonic","lavender",
    "leather","mossy","musky","ozonic","powdery","rose","smoky","sweet","tobacco",
    "tropical","tuberose","vanilla","violet","warm spicy","whiskey","white floral",
    "woody","yellow floral"
]
NOTE_NAMES      = [
    "agarwood (oud)","aldehydes","almond","amalfi lemon","amber","ambergris","ambroxan",
    "apple","apricot","artemisia","australian sandalwood","basil","beeswax","benzoin",
    "bergamot","big strawberry","birch leaf","bitter orange","black amber","black currant",
    "black pepper","black tea","blood orange","broom","bulgarian rose","calabrian bergamot",
    "calone","candy apple","cannabis","caramel","caraway","cardamom","carnation",
    "casablanca lily","cashmeran","cashmere wood","cedar","ceylon cinnamon","cherry",
    "chestnut","chocolate","cinnamon","cinnamon leaf","citruses","civet","clementine",
    "clove","coconut","coffee","coriander","coriander extract","cypress","dried plum",
    "floral notes","fruity notes","gardenia","geranium","ginger","ginger flower",
    "grapefruit","grasse rose","green mandarin","green notes","heliotrope","hibiscus",
    "honey","honeysuckle","hyacinth","incense","indian tuberose","indonesian patchouli leaf",
    "iris","jasmine","jasmine sambac","juniper","laurels","lavender","leather","lemon",
    "lily","lily-of-the-valley","litchi","lotus","madagascar vanilla","madagascar ylang-ylang",
    "magnolia","mandarin orange","mango","may rose","mimosa","mint","mirabilis","moss",
    "musk","myrrh","narcissus","neroli","nutmeg","oakmoss","olive blossom","orange",
    "orange blossom","orris","passionfruit","patchouli","peach","pear","peony","pepper",
    "peru balsam","petitgrain","pine tree","pineapple","pink pepper","pistachio","plum",
    "powdery notes","raspberry","red berries","red currant","red fruits","rice","rose",
    "rosebay willowherb","rosemary","rum","saffron","sage","salt","sandalwood",
    "silkwood blossom","star anise","suede","sugar","tahitian vanilla","tangerine","tea",
    "texas cedar","tiare flower","tobacco","tobacco leaf","tonka bean","tuberose",
    "tunisian neroli","turkish rose","vanilla","vanille","vetiver","vetyver","violet",
    "violet leaf","virginia cedar","water mint","west indian bay","whipped cream","whiskey",
    "white honey","white musk","white peach","white pepper","white woods","woodsy notes",
    "woody notes","ylang-ylang"
]

# -------------------------
# Maps (case-insensitive keys)
# -------------------------
gender_to_idx    = {n.lower():i for i,n in enumerate(GENDER_NAMES)}
brand_to_idx     = {n.lower():i for i,n in enumerate(BRAND_NAMES)}
sillage_to_idx   = {n.lower():i for i,n in enumerate(SILLAGE_NAMES)}
longevity_to_idx = {n.lower():i for i,n in enumerate(LONGEVITY_NAMES)}
price_to_idx     = {n.lower():i for i,n in enumerate(PRICE_NAMES)}
accord_to_idx    = {n.lower():i for i,n in enumerate(ACCORD_NAMES)}
note_to_idx      = {n.lower():i for i,n in enumerate(NOTE_NAMES)}

# -------------------------
# Helpers
# -------------------------
def gen_csv(gender, brand, notes, accords, sillage, longevity, price):
    gender = (gender or "Any")
    brand  = (brand  or "Any")
    sillage = (sillage or "Any")
    longevity = (longevity or "Any")
    price = (price or "Any")

    g = gender_to_idx.get(gender.lower(), -1) if gender != "Any" else -1
    b = brand_to_idx.get(brand.lower(), -1) if brand != "Any" else -1
    s = sillage_to_idx.get(sillage.lower(), -1) if sillage != "Any" else -1
    l = longevity_to_idx.get(longevity.lower(), -1) if longevity != "Any" else -1
    p = price_to_idx.get(price.lower(), -1) if price != "Any" else -1

    notes_part = ":".join(
        str(note_to_idx[n.strip().lower()]) for n in (notes or []) 
        if isinstance(n, str) and n.strip().lower() in note_to_idx
    )
    accords_part = ":".join(
        str(accord_to_idx[a.strip().lower()]) for a in (accords or [])
        if isinstance(a, str) and a.strip().lower() in accord_to_idx
    )

    return f"PREF,{g},{b},{notes_part},{accords_part},{s},{l},{p}"

# -------------------------
# GPIO LED mapping & setup
# -------------------------
# Mapping perfume ID -> BCM GPIO pin
PERFUME_GPIO_MAP = {
    "P001": 22,  # alien
    "P030": 23,  # geranium
    "P020": 24,  # bee
    "P047": 25,  # gardenia
    "P049": 5,   # incanto
    "P007": 6,   # amber
    "P017": 12,  # Gucci
    "P045": 13,  # braze
    "P026": 19,  # sexy
    "P005": 26,  # gucci-bamboo
}

# Duration to keep LED on (seconds)
LED_ON_DURATION = 10.0

# Try import RPi.GPIO, otherwise disable GPIO features gracefully
gpio_available = True
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    # setup pins
    for pin in set(PERFUME_GPIO_MAP.values()):
        try:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        except Exception as e:
            print(f"[GPIO Warn] Không thể setup pin {pin}: {e}")
except Exception as e:
    gpio_available = False
    print("[GPIO Warn] RPi.GPIO không khả dụng, sẽ bỏ qua phần điều khiển LED. Lỗi:", e)

def _turn_off_pins(pins):
    if not gpio_available:
        return
    for p in pins:
        try:
            GPIO.output(p, GPIO.LOW)
        except Exception as ex:
            print(f"[GPIO Warn] Lỗi tắt pin {p}: {ex}")

def light_matched_leds(ids, duration=LED_ON_DURATION):
    """
    ids: list of strings like ['P001', 'P023', ...]
    duration: seconds to keep LED on
    Hành vi: bật HIGH các pin tương ứng, sau `duration` sẽ tắt lại (không block thread chính).
    """
    if not gpio_available:
        # nếu RPi.GPIO không có, chỉ log ra
        print("[GPIO] GPIO không khả dụng => bỏ qua việc bật LED. Matched IDs:", ids)
        return

    pins_to_turn_on = []
    for pid in ids:
        if not isinstance(pid, str):
            continue
        key = pid.strip().upper()
        if key in PERFUME_GPIO_MAP:
            pins_to_turn_on.append(PERFUME_GPIO_MAP[key])

    if not pins_to_turn_on:
        # không có pin khớp
        return

    # Bật các pin (HIGH)
    for p in pins_to_turn_on:
        try:
            GPIO.output(p, GPIO.HIGH)
        except Exception as ex:
            print(f"[GPIO Warn] Lỗi bật pin {p}: {ex}")

    # Lên lịch tắt các pin sau `duration` giây (không block)
    try:
        t = threading.Timer(duration, _turn_off_pins, args=(pins_to_turn_on,))
        t.daemon = True
        t.start()
    except Exception as e:
        print("[GPIO Warn] Không thể lên lịch tắt pin:", e)

# -------------------------
# Redis + UART setup
# -------------------------
redis_client = redis.Redis(host='localhost', port=6379, db=0)

UART_DEVICE = "/dev/serial0"
UART_BAUDRATE = 115200

try:
    ser = serial.Serial(UART_DEVICE, baudrate=UART_BAUDRATE, timeout=1)
except Exception as e:
    print("Không thể mở cổng UART:", e)
    sys.exit(1)

# -------------------------
# Thread: read from UART
# -------------------------
def read_from_uart():
    try:
        while True:
            try:
                rx_data = ser.readline().decode(errors="ignore").strip()
                if rx_data:
                    print(f"\nRX: {rx_data}")

                    key = "RESULT,"
                    idx = rx_data.upper().find(key)
                    if idx != -1:
                        tail = rx_data[idx + len(key):].lstrip()
                        tokens = [t.strip() for t in tail.split(",") if t.strip() != ""]

                        ids = []
                        for i in range(0, len(tokens), 2):
                            m = re.search(r'[-+]?\d+', tokens[i])
                            if m:
                                try:
                                    num = int(m.group())
                                    num += 1
                                    ids.append(f"P{num:03d}")
                                except Exception as e:
                                    print(f"[Warn] Không convert được '{m.group()}' -> int:", e)

                        if ids:
                            try:
                                # Bật LED tương ứng (nếu có) TRƯỚC khi lưu vào Redis
                                try:
                                    light_matched_leds(ids)
                                except Exception as ex_light:
                                    print("[Warn] Lỗi khi bật LED:", ex_light)

                                redis_client.set("uart_model_result", ids[0])
                                if len(ids) > 1:
                                    redis_client.set("uart_model_result_2", ids[1])
                                else:
                                    redis_client.delete("uart_model_result_2")
                                if len(ids) > 2:
                                    redis_client.set("uart_model_result_3", ids[2])
                                else:
                                    redis_client.delete("uart_model_result_3")
                                redis_client.set("uart_model_result_all", json.dumps(ids))
                            except Exception as e:
                                print("Lỗi lưu Redis:", e)

                            # Lưu thêm confidence của top1
                            try:
                                if len(tokens) >= 2:
                                    conf1 = float(tokens[1])  # token[1] là confidence của id đầu tiên
                                    redis_client.set("uart_model_confidence", conf1)
                                else:
                                    redis_client.delete("uart_model_confidence")
                            except Exception as e:
                                print("Lỗi parse confidence:", e)
                                redis_client.delete("uart_model_confidence")

                            print(f"[Parsed] top1 -> {ids[0]} ; top2/3 -> {ids[1:3] if len(ids)>1 else []}")
            except Exception:
                traceback.print_exc()
                time.sleep(0.5)
    except Exception:
        traceback.print_exc()

# -------------------------
# Thread: poll Redis -> UART
# -------------------------
REDIS_KEY = "uart_outgoing_message"
POLL_INTERVAL = 0.5

def redis_poller():
    try:
        while True:
            raw = redis_client.get(REDIS_KEY)
            if raw:
                try:
                    s = raw.decode('utf-8') if isinstance(raw, bytes) else str(raw)
                    data = json.loads(s.strip())
                except Exception as e:
                    print("Không parse được JSON:", e, "Raw:", raw)
                    time.sleep(POLL_INTERVAL)
                    continue

                def get_field(d, *keys, default=None):
                    for k in keys:
                        if k in d:
                            return d[k]
                    for kk in d:
                        if kk.lower() in [k.lower() for k in keys]:
                            return d[kk]
                    return default

                # Lấy fields theo chuẩn build_request_json
                gender   = get_field(data, "gender", default="Any")
                brand    = get_field(data, "brand", default="Any")
                notes    = get_field(data, "notes", default=[])
                accords  = get_field(data, "preferred_accord", "accords", default=[])
                sillage  = get_field(data, "sillage", default="Any")
                longevity= get_field(data, "longevity", default="Any")
                price    = get_field(data, "price", default="Any")

                if isinstance(notes, str):
                    notes = [x.strip() for x in notes.split(",") if x.strip()]
                if isinstance(accords, str):
                    accords = [x.strip() for x in accords.split(",") if x.strip()]

                try:
                    csv_line = gen_csv(gender, brand, notes, accords, sillage, longevity, price)
                except Exception as e:
                    print("Lỗi tạo CSV:", e)
                    csv_line = None

                if csv_line:
                    try:
                        ser.write((csv_line + "\n").encode())
                        print(f"--> Gửi qua UART: {csv_line}")
                    except Exception as e:
                        print("Lỗi UART:", e)

            time.sleep(POLL_INTERVAL)
    except Exception:
        traceback.print_exc()

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    t_uart = threading.Thread(target=read_from_uart, daemon=True)
    t_poll = threading.Thread(target=redis_poller, daemon=True)
    t_uart.start()
    t_poll.start()

    print("UART terminal started. Gõ gì sẽ gửi qua UART. (Ctrl+C để thoát)")
    try:
        while True:
            msg = input("> ")
            if msg:
                ser.write((msg + "\n").encode())
    except KeyboardInterrupt:
        print("\nThoát terminal.")
    finally:
        try:
            ser.close()
        except Exception:
            pass
        # cleanup GPIO nếu có
        if gpio_available:
            try:
                GPIO.cleanup()
            except Exception:
                pass
        print("Closed UART. Bye.")
