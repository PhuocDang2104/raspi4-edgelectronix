#!/usr/bin/env python3
"""
uart_redis_csv_sender.py
- Terminal UART interactive (gõ gửi)
- Background thread: poll Redis key 'uart_outgoing_message' (contains JSON bytes),
  convert to PREF CSV line (same format as gen_csv in your GUI) and send via UART.
"""

import serial
import threading
import redis
import json
import time
import sys
import traceback

# -------------------------
# Vocabularies (same as GUI)
# -------------------------
GENDER_NAMES    = ["men", "unisex", "women"]
BRAND_NAMES     = [
    "antonio-puig","avon","balenciaga","bdk-parfums","burberry","bvlgari","by-kilian",
    "carolina-herrera","cerruti","coty","escada","fragonard","frederic-malle","givenchy",
    "goldfield-banks-australia","guerlain","hugo-boss","iceberg","issey-miyake",
    "jean-paul-gaultier","juicy-couture","kenneth-cole","lacoste-fragrances","lalique",
    "lancome","lanvin","lorenzo-villoresi","montblanc","mugler","narciso-rodriguez",
    "natura","paco-rabanne","the-body-shop","trussardi","vilhelm-parfumerie","xerjoff",
    "yves-saint-laurent","zadig-voltaire","zara","zoologist-perfumes"
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
    # Normalize input (None -> "Any")
    gender = (gender or "Any")
    brand  = (brand  or "Any")
    sillage = (sillage or "Any")
    longevity = (longevity or "Any")
    price = (price or "Any")

    # Any -> -1 mapping, case-insensitive lookup
    g = gender_to_idx.get(gender.lower(), -1) if gender != "Any" else -1
    b = brand_to_idx.get(brand.lower(), -1) if brand != "Any" else -1
    s = sillage_to_idx.get(sillage.lower(), -1) if sillage != "Any" else -1
    l = longevity_to_idx.get(longevity.lower(), -1) if longevity != "Any" else -1
    p = price_to_idx.get(price.lower(), -1) if price != "Any" else -1

    # notes and accords are lists of strings; match case-insensitively and ignore unknowns
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
# Redis + UART setup
# -------------------------
# Redis config - adjust host/port/db if needed
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# UART: change device path if on Windows or different port
UART_DEVICE = "/dev/serial0"   # example for Raspberry Pi; on Windows use "COM3" etc.
UART_BAUDRATE = 115200

try:
    ser = serial.Serial(UART_DEVICE, baudrate=UART_BAUDRATE, timeout=1)
except Exception as e:
    print("Không thể mở cổng UART:", e)
    sys.exit(1)

# -------------------------
# Thread: read from UART and print incoming lines
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
                        # phần sau RESULT,
                        tail = rx_data[idx + len(key):].lstrip()
                        # tách theo dấu phẩy, bỏ rỗng
                        tokens = [t.strip() for t in tail.split(",") if t.strip() != ""]

                        ids = []
                        # các token ở vị trí 0,2,4,... là id theo format của bạn
                        for i in range(0, len(tokens), 2):
                            num_token = tokens[i]
                            m = re.search(r'[-+]?\d+', num_token)
                            if m:
                                try:
                                    num = int(m.group())
                                    ids.append(f"P{num:03d}")
                                except Exception as e:
                                    print(f"[Warn] Không thể convert '{m.group()}' -> int:", e)
                            else:
                                print(f"[Warn] Không tìm thấy số trong token id: '{num_token}'")

                        if len(ids) == 0:
                            print("[Info] Không tìm thấy id hợp lệ sau 'RESULT,'")
                        else:
                            # 1) giữ tương thích: uart_model_result -> top1 (string)
                            top1 = ids[0]
                            try:
                                redis_client.set("uart_model_result", top1)
                            except Exception as e:
                                print("Lỗi khi lưu top1 vào Redis:", e)

                            # 2) lưu top2 / top3 vào key khác (hoặc xóa nếu không có)
                            try:
                                if len(ids) > 1:
                                    redis_client.set("uart_model_result_2", ids[1])
                                else:
                                    redis_client.delete("uart_model_result_2")

                                if len(ids) > 2:
                                    redis_client.set("uart_model_result_3", ids[2])
                                else:
                                    redis_client.delete("uart_model_result_3")
                            except Exception as e:
                                print("Lỗi khi lưu top2/top3 vào Redis:", e)

                            # 3) optional: lưu toàn bộ mảng dưới dạng JSON (tiện cho frontend nếu muốn)
                            try:
                                redis_client.set("uart_model_result_all", json.dumps(ids))
                            except Exception as e:
                                print("Lỗi khi lưu result_all vào Redis:", e)

                            print(f"[Parsed] top1 -> {top1} ; top2/3 -> {ids[1:3] if len(ids)>1 else []}")
                    else:
                        print("[Info] Không tìm thấy 'RESULT,<num>' trong dòng nhận được.")
            except Exception:
                traceback.print_exc()
                time.sleep(0.5)
    except Exception:
        traceback.print_exc()

# -------------------------
# Thread: poll Redis key, convert JSON -> PREF CSV, send via UART
# -------------------------
REDIS_KEY = "uart_outgoing_message"
POLL_INTERVAL = 0.5  # seconds

def redis_poller():
    try:
        while True:
            try:
                raw = redis_client.get(REDIS_KEY)
            except Exception as e:
                print("Lỗi khi đọc Redis:", e)
                raw = None

            if raw:
                # raw is bytes (b'...'), decode to str
                try:
                    if isinstance(raw, bytes):
                        s = raw.decode('utf-8', errors='ignore')
                    else:
                        s = str(raw)
                    # If Redis stored a Python repr like b'{"..."}' (rare), strip leading b' and trailing '
                    # But usually it's a plain JSON string bytes.
                    s = s.strip()
                    # parse JSON
                    data = json.loads(s)
                except Exception as e:
                    print("Không parse được JSON từ Redis value:", e)
                    print("Raw value:", raw)
                    # remove bad key to avoid spinning on bad content
                    try:
                        redis_client.delete(REDIS_KEY)
                    except Exception:
                        pass
                    time.sleep(POLL_INTERVAL)
                    continue

                # Extract fields (case-insensitive keys possible)
                # Try upper-case keys first (since your example uses uppercase keys), else lower-case
                def get_field(d, *keys, default=None):
                    for k in keys:
                        if k in d:
                            return d[k]
                    # case-insensitive
                    for kk in d:
                        if kk.lower() in [k.lower() for k in keys]:
                            return d[kk]
                    return default

                gender = get_field(data, "GENDER", "gender", default="Any")
                brand  = get_field(data, "BRAND", "brand", default="Any")
                notes  = get_field(data, "NOTES", "notes", default=[])
                accords= get_field(data, "PREFERRED_ACCORD", "PREFERRED_ACCORDS", "preferred_accord", "preferred_accords", "accords", default=[])
                sillage= get_field(data, "SILLAGE", "sillage", default="Any")
                longevity = get_field(data, "LONGEVITY", "longevity", default="Any")
                price  = get_field(data, "PRICE", "price", default="Any")

                # Ensure lists
                if isinstance(notes, str):
                    # maybe comma-separated
                    notes = [x.strip() for x in notes.split(",") if x.strip()]
                if isinstance(accords, str):
                    accords = [x.strip() for x in accords.split(",") if x.strip()]

                # Generate CSV line
                try:
                    csv_line = gen_csv(gender, brand, notes, accords, sillage, longevity, price)
                except Exception as e:
                    print("Lỗi khi tạo CSV:", e)
                    csv_line = None

                if csv_line:
                    try:
                        ser.write((csv_line + "\n").encode())
                        print(f"--> Gửi qua UART: {csv_line}")
                    except Exception as e:
                        print("Lỗi khi gửi UART:", e)

                # Remove key so we don't resend
                try:
                    redis_client.delete(REDIS_KEY)
                except Exception as e:
                    print("Không xóa được key Redis:", e)

            time.sleep(POLL_INTERVAL)
    except Exception:
        traceback.print_exc()

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    # start threads
    t_uart = threading.Thread(target=read_from_uart, daemon=True)
    t_poll = threading.Thread(target=redis_poller, daemon=True)
    t_uart.start()
    t_poll.start()

    print("UART terminal started. Gõ gì sẽ gửi qua UART. (Ctrl+C để thoát)")
    try:
        while True:
            msg = input("> ")
            if msg:
                try:
                    ser.write((msg + "\n").encode())
                except Exception as e:
                    print("Lỗi gửi UART:", e)
    except KeyboardInterrupt:
        print("\nThoát terminal.")
    finally:
        try:
            ser.close()
        except Exception:
            pass
        print("Closed UART. Bye.")


