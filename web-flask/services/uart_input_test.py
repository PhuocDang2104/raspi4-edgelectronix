#!/usr/bin/env python3
"""
redis_csv_debugger.py
- Không dùng UART
- Poll Redis key 'uart_outgoing_message'
- Parse JSON -> convert thành CSV PREF line
- Chỉ in ra console (thay vì gửi UART)
"""

import redis
import json
import time
import traceback
import re

# -------------------------
# Vocabularies
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
# Maps
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
    g = gender_to_idx.get((gender or "Any").lower(), -1) if gender != "Any" else -1
    b = brand_to_idx.get((brand or "Any").lower(), -1) if brand != "Any" else -1
    s = sillage_to_idx.get((sillage or "Any").lower(), -1) if sillage != "Any" else -1
    l = longevity_to_idx.get((longevity or "Any").lower(), -1) if longevity != "Any" else -1
    p = price_to_idx.get((price or "Any").lower(), -1) if price != "Any" else -1

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
# Redis setup
# -------------------------
redis_client = redis.Redis(host='localhost', port=6379, db=0)

REDIS_KEY = "uart_outgoing_message"
POLL_INTERVAL = 0.5

def redis_poller():
    while True:
        try:
            raw = redis_client.get(REDIS_KEY)
            if raw:
                try:
                    s = raw.decode('utf-8') if isinstance(raw, bytes) else str(raw)
                    data = json.loads(s.strip())
                except Exception as e:
                    print("Không parse được JSON:", e, "Raw:", raw)
                    redis_client.delete(REDIS_KEY)
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

                is_ai_nlp = all(k in data for k in ("preferred_accord", "longevity", "price"))

                if is_ai_nlp:
                    gender = "Any"
                    brand  = "Any"
                    sillage= "Any"
                    accords = data.get("preferred_accord", [])
                    longevity = data.get("longevity", "Any")
                    price = data.get("price", "Any")

                    if isinstance(accords, str):
                        accords = [x.strip() for x in accords.split(",") if x.strip()]
                    notes = accords.copy()
                else:
                    gender = get_field(data, "GENDER", "gender", default="Any")
                    brand  = get_field(data, "BRAND", "brand", default="Any")
                    notes  = get_field(data, "NOTES", "notes", default=[])
                    accords= get_field(data, "PREFERRED_ACCORD", "preferred_accord", "accords", default=[])
                    sillage= get_field(data, "SILLAGE", "sillage", default="Any")
                    longevity = get_field(data, "LONGEVITY", "longevity", default="Any")
                    price  = get_field(data, "PRICE", "price", default="Any")

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
                    print("[UART OUT]", csv_line)

                redis_client.delete(REDIS_KEY)
        except Exception:
            traceback.print_exc()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    print("Redis CSV Debugger started. Listening for key:", REDIS_KEY)
    redis_poller()
