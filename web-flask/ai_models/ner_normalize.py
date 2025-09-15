# ner_normalizer.py

def build_reverse_map(category_dict):
    reverse_map = {}
    for key, value in category_dict.items():
        if isinstance(value, dict):  # handle nested dict (e.g., sillage, longevity)
            for sublist in value.values():
                for phrase in sublist:
                    reverse_map[phrase.lower()] = key
        else:  # flat list
            for phrase in value:
                reverse_map[phrase.lower()] = key
    return reverse_map

# manual accord -> notes map (canonical note names, lower-case)
ACCORD_TO_NOTES_MANUAL = {
    "floral": [
        "rose",
        "jasmine",
        "peony",
        "geranium",
        "gardenia",
        "hyacinth",
        "carnation",
        "may rose"
    ],
    "white floral": [
        "jasmine sambac",
        "jasmine",
        "tuberose",
        "neroli",
        "lily",
        "lily-of-the-valley",
        "orange blossom",
        "lotus",
        "white honey"
    ],
    "yellow floral": [
        "magnolia",
        "tiare flower",
        "may rose",
        "honeysuckle"
    ],
    "woody": [
        "cedar",
        "sandalwood",
        "vetiver",
        "pine tree",
        "texas cedar",
        "virginia cedar",
        "woodsy notes",
        "woody notes",
        "oakmoss"
    ],
    "earthy": [
        "patchouli",
        "indonesian patchouli leaf",
        "moss",
        "vetiver",
        "oakmoss"
    ],
    "mossy": [
        "oakmoss",
        "moss"
    ],
    "citrus": [
        "bergamot",
        "calabrian bergamot",
        "lemon",
        "orange",
        "grapefruit",
        "mandarin orange",
        "tangerine",
        "clementine",
        "green mandarin",
        "petitgrain"
    ],
    "sweet": [
        "vanilla",
        "caramel",
        "tonka bean",
        "almond",
        "whipped cream",
        "sugar",
        "coconut"
    ],
    "powdery": [
        "iris",
        "heliotrope",
        "mimosa",
        "violet",
        "powdery notes",
        "orris"
    ],
    "balsamic": [
        "benzoin",
        "myrrh",
        "peru balsam",
        "incense"
    ],
    "amber": [
        "amber",
        "ambergris",
        "ambroxan",
        "black amber"
    ],
    "vanilla": [
        "vanilla",
        "madagascar vanilla",
        "tahitian vanilla"
    ],
    "fruity": [
        "apple",
        "apricot",
        "big strawberry",
        "black currant",
        "dried plum",
        "litchi",
        "peach",
        "pear",
        "raspberry",
        "mango",
        "pineapple",
        "cherry",
        "strawberry"
    ],
    "tropical": [
        "pineapple",
        "mango",
        "coconut",
        "tiare flower",
        "passionfruit",
        "ylang-ylang",
        "hibiscus"
    ],
    "spicy": [
        "cinnamon",
        "clove",
        "cardamom",
        "black pepper",
        "pink pepper",
        "nutmeg",
        "ginger",
        "star anise",
        "saffron"
    ],
    "warm spicy": [
        "cinnamon",
        "clove",
        "saffron",
        "nutmeg",
        "benzoin"
    ],
    "fresh spicy": [
        "white pepper",
        "pink pepper",
        "ginger",
        "black pepper"
    ],
    "aromatic": [
        "rosemary",
        "tea",
        "black tea",
        "laurels"
    ],
    "green": [
        "green notes",
        "mint",
        "water mint",
        "juniper"
    ],
    "aquatic": [
        "calone",
        "lotus"
    ],
    "ozonic": [
        "calone",
        "salt"
    ],
    "musky": [
        "musk",
        "white musk"
    ],
    "animalic": [
        "civet"
    ],
    "leather": [
        "leather",
        "suede"
    ],
    "smoky": [
        "incense",
        "birch leaf",
        "tobacco"
    ],
    "aldehydic": [
        "aldehydes"
    ],
    "coffee": [
        "coffee"
    ],
    "lactonic": [
        "whipped cream"
    ],
    "iris": [
        "iris",
        "orris"
    ],
    "violet": [
        "violet",
        "violet leaf"
    ],
    "rose": [
        "rose",
        "turkish rose",
        "grasse rose",
        "bulgarian rose"
    ],
    "tuberose": [
        "tuberose",
        "indian tuberose"
    ],
    "lavender": [
        "lavender"
    ],
    "herbal": [
        "basil",
        "sage",
        "rosemary",
        "artemisia"
    ],
    "beeswax": [
        "beeswax",
        "white honey"
    ],
    "honey": [
        "honey",
        "white honey"
    ],
    "whiskey": [
        "whiskey",
        "rum"
    ],
    "cannabis": [
        "cannabis"
    ],
    "cherry": [
        "cherry"
    ],
    "tobacco": [
        "tobacco",
        "tobacco leaf"
    ],
    "chocolate": [
        "chocolate",
        "cocoa",
        "dark chocolate"
    ]
}
# -------------------------
# Mapping từ synonyms sang nhãn gốc
# -------------------------
gender_map = {
    "men": ["man", "boy", "male", "gentleman", "guy"],
    "women": ["woman", "girl", "female", "lady"],
    "unisex": ["unisex", "non-binary", "gender-neutral", "both genders", "undefined", "unidentified"]
}

personality_map = {
    "elegant": ["elegant", "graceful", "refined", "formal", "gentle"],
    "sporty": ["sporty", "athletic", "active"],
    "bold": ["bold", "confident", "daring"],
    "classic": ["classic", "timeless", "vintage", "retro"],
    "romantic": ["romantic", "loving", "affectionate", "tender", "passionate"],
    "artistic": ["artistic", "creative", "expressive", "imaginative"],
    "modern": ["modern", "trendy", "contemporary", "fashion-forward"],
    "minimalist": ["minimalist", "simple", "understated", "clean", "plain"],
    "natural": ["natural", "earthy", "organic", "pure"],
    "youthful": ["youthful", "vibrant", "energetic", "lively"],
    "casual": ["casual", "relaxed", "laid-back", "easygoing"],
    "mysterious": ["mysterious", "enigmatic", "intriguing", "elusive"]
}

# Accord map full synonyms (đã khớp ACCORD_NAMES, không thừa thiếu)
accord_map = {
    "floral": ["floral", "flowery", "flower", "blooming", "blossom", "petal-like", "bouquet", "broom", "geranium", "peony", "mirabilis", "rosebay willowherb", "floral notes", "gardenia", "hyacinth", "carnation", "pink pepper"],
    "white floral": ["white floral", "delicate floral", "white flower", "soft floral", "pure bloom", "creamy flower", "jasmine-like", "jasmine", "jasmine sambac", "lily", "lily-of-the-valley", "orange blossom", "neroli", "tuberose", "indian tuberose", "magnolia", "narcissus", "casablanca lily", "honeysuckle", "lotus", "white honey"],
    "yellow floral": ["yellow floral", "bright floral", "colorful flower", "sunny bloom", "golden flower", "cheerful floral", "sunflower"],
    "woody": ["woody", "oak", "wood", "tree", "bark", "cedar", "piney", "dry wood", "forest", "pine tree", "agarwood (oud)", "australian sandalwood", "cashmeran", "cashmere wood", "cypress", "cedar", "sandalwood", "texas cedar", "virginia cedar", "woodsy notes", "woody notes", "white woods", "pine tree", "birch leaf", "vetiver", "vetyver", "oakmoss"],
    "earthy": ["earthy", "soil-like", "groundy", "damp earth", "natural", "humus", "clay", "soil", "patchouli", "indonesian patchouli leaf", "moss"],
    "mossy": ["mossy", "green moss", "moss", "oakmoss"],
    "citrus": ["citrus", "citrusy", "zesty", "lemony", "lime", "grapefruit", "tart", "fresh peel", "bitter orange", "blood orange", "clementine", "mandarin orange", "orange", "bergamot", "calabrian bergamot", "bergamot", "green mandarin", "mandarin orange", "tangerine", "amalfi lemon", "lemon", "citruses", "petitgrain"],
    "sweet": ["sweet", "sugary", "candied", "chocolate", "dark chocolate", "cocoa", "whipped cream", "dessert-like", "syrupy", "salted caramel", "caramel", "almond", "candy apple", "tonka bean", "sugar", "pistachio", "rum", "coconut", "chestnut"],
    "powdery": ["powdery", "soft powder", "heliotrope", "mimosa", "powdery notes", "rice", "silkwood blossom"],
    "balsamic": ["balsamic", "resinous", "syrupy", "benzoin", "myrrh", "peru balsam", "incense"],
    "amber": ["amber", "warm", "resinous", "ambergris", "ambroxan", "black amber"],
    "vanilla": ["vanilla", "creamy", "sweet vanilla", "madagascar vanilla", "tahitian vanilla", "vanille"],
    "fruity": ["fruity", "juicy", "fruit-like", "apple", "apricot", "big strawberry", "black currant", "dried plum", "litchi", "passionfruit", "peach", "pear", "plum", "raspberry", "red berries", "red currant", "red fruits", "white peach", "mango", "pineapple", "tropical", "cherry", "strawberry"],
    "tropical": ["tropical", "island vibe", "exotic fruit", "beachy", "pineapple", "mango", "coconut", "tiare flower", "passionfruit", "hibiscus", "madagascar ylang-ylang", "ylang-ylang"],
    "spicy": ["spicy", "peppery", "hot", "ginger", "ginger flower", "ceylon cinnamon", "saffron", "cardamom", "black pepper", "pink pepper", "nutmeg", "star anise", "clove", "coriander", "caraway"],
    "warm spicy": ["warm spicy", "cozy spice", "rich spice", "cinnamon-like", "amber spice", "comforting", "cinnamon", "ceylon cinnamon", "clove", "saffron", "nutmeg"],
    "fresh spicy": ["fresh spicy", "zingy spice", "green spice", "white pepper", "pink pepper", "ginger"],
    "aromatic": ["aromatic", "herbal", "medicinal", "black tea", "tea", "rosemary"],
    "green": ["green", "leafy", "grassy", "green notes", "mint", "juniper", "water mint"],
    "aquatic": ["aquatic", "marine", "watery", "sea", "ocean", "fresh water", "calone", "lotus"],
    "ozonic": ["ozonic", "airy", "clean", "cool breeze", "mountain air", "clean breeze", "salt"],
    "musky": ["musky", "animalic", "skin-like", "white musk", "musk"],
    "animalic": ["animalic", "feral", "musk-like", "civet"],
    "leather": ["leather", "suede", "tanned hide"],
    "smoky": ["smoky", "burnt", "charcoal", "campfire", "smoky tobacco", "incense", "birch leaf"],
    "aldehydic": ["aldehydic", "soapy", "metallic", "soap", "aldehydes"],
    "coffee": ["coffee", "roasted", "caffeinated", "espresso", "bitter-sweet", "americano", "roasted coffee"],
    "lactonic": ["lactonic", "milky", "creamy"],
    "iris": ["iris", "powdery floral", "rooty floral", "buttery flower", "orris"],
    "violet": ["violet", "sweet floral", "purple flower", "powdery violet", "candy floral", "violet leaf"],
    "rose": ["rose", "rosy", "romantic floral", "red flower", "velvety petal", "floral heart", "bulgarian rose", "turkish rose", "may rose", "grasse rose"],
    "tuberose": ["tuberose", "heady floral", "white bloom", "indian tuberose"],
    "lavender": ["lavender", "soothing herb", "purple herb"],
    "herbal": ["herbal", "green plant", "botanical", "plant", "basil", "sage", "laurels", "rosemary", "artemisia"],
    "beeswax": ["beeswax", "waxen", "honeyed wax"],
    "honey": ["honey", "sweet nectar", "bee-sweet", "white honey"],
    "whiskey": ["whiskey", "boozy", "aged alcohol", "alcohol", "liquor", "brandy", "rum"],
    "cannabis": ["cannabis", "weed-like", "green narcotic", "hemp"],
    "cherry": ["cherry", "red fruit", "sweet cherry", "berry", "sakura"],
    "tobacco": ["tobacco", "smoked leaf", "nicotine scent", "burnt", "charcoal", "campfire", "cigarette", "tobacco leaf"],
    "chocolate": ["chocolate", "cacao", "cocoa", "dark chocolate", "milk chocolate"],
}

# -------------------------
# NOTE_NAMES (full) & note_map for direct detection
# -------------------------
NOTE_NAMES = [
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

# Build a simple note_map (canonical note -> synonyms list). Here we keep canonical = note itself.
note_map = { n.lower(): [n.lower()] for n in NOTE_NAMES }
rev_note_map = build_reverse_map(note_map)


usage_map = {
    "Work": [
        "for work",
        "at the office",
        "during working hours",
        "in professional settings",
        "for business-related occasions",
        "when i go to work"
    ],
    "Casual": [
        "for casual outings",
        "on relaxed days",
        "for informal hangouts",
        "during laid-back times",
        "when dressing down",
        "for daily",
        "on normal days"
    ],
    "Date Night": [
        "for a romantic night out",
        "on a date night",
        "for romantic occasions",
        "during intimate evenings",
        "for date nights",
        "when going out with someone special",
        "for dating",
        "on a date"
    ],
    "Formal": [
        "for formal events",
        "at formal gatherings",
        "during elegant occasions",
        "for black-tie events",
        "in ceremonial settings"
        "for formal party",
        "when go to formal party"
    ],
    "Everyday": [
        "for daily wear",
        "on a regular basis",
        "for everyday use",
        "as a go-to scent",
        "for routine days",
        "on a daily basis",
        "normal days"
    ],
    "Gym": [
        "at the gym",
        "while working out",
        "during fitness sessions",
        "in exercise routines",
        "when staying active"
    ],
    "Vacation": [
        "while traveling",
        "on vacation",
        "during trips",
        "for getaways",
        "on holidays",
        "when i travel"
    ],
    "Outdoor Activities": [
        "for outdoor activities",
        "while being active outside",
        "during nature adventures",
        "on hikes or walks",
        "in open-air events",
        "for activities",
        "when playing sports",
        "for playing sports",
        "when playing sports",
        "for playing basketball",
        "for playing football",
        "for tennis"
    ],
    "Party": [
        "at parties",
        "for party",
        "at party",
        "for parties",
        "when clubbing",
        "during nightlife",
        "on nights out",
        "for dancing events",
        "for partying",
        "for clubbing",
        "when i go to",
    ],
    "Relaxing at Home": [
        "when relaxing at home",
        "during downtime",
        "on lazy days",
        "in cozy moments",
        "while staying in"
    ]
}


sillage_phrases = {
    "Light": {
        "noun": ["light sillage", "a subtle trail", "soft projection", "soft sillage", "a faint scent trail", "a barely noticeable presence"],
        "verb": ["has a soft trail","projects subtly", "leaves a soft trail", "is barely noticeable", "fades quickly into the background"]
    },
    "Medium": {
        "noun": ["medium sillage", "moderate sillage", "balanced projection", "a decent scent trail", "a noticeable but not overwhelming trail", "medium presence"],
        "verb": ["projects moderately", "leaves a balanced trail", "is noticeable but not overwhelming", "lingers with decent strength"]
    },
    "Strong": {
        "noun": ["strong sillage", "a powerful scent trail", "bold projection", "a lingering presence", "a prominent scent", "dense sillage"],
        "verb": ["projects boldly", "leaves a powerful scent trail", "fills the air with a noticeable presence", "is strong and persistent"]
    },
    "Very Strong": {
        "noun": ["very strong sillage", "an intense scent trail", "overpowering projection", "a room-filling aroma", "a room-filling projection", "a room-filling sillage", "an extremely dense sillage"],
        "verb": ["fills the room instantly", "projects intensely", "overpowers the surroundings", "is extremely strong and room-filling"]
    }
}


longevity_phrases = {
    "Short": {
        "noun": ["short longevity", "quick fade", "brief lasting power", "light staying power", "low durability"],
        "verb": ["fades quickly", "doesn't last long", "wears off soon", "loses scent fast"]
    },
    "Medium": {
        "noun": ["medium longevity", "moderate staying power", "a decent wear time", "balanced longevity", "noticeable duration"],
        "verb": ["doesn't fade so quickly", "lasts a decent time", "stays on fairly well", "lingers moderately", "holds through a few hours"]
    },
    "Long": {
        "noun": ["long longevity", "good longevity", "long-lasting scent", "strong longevity", "all-day wear", "extended staying power", "persistent performance"],
        "verb": ["lasts all day", "lasts long", "lasts very long", "lasts extremely long", "lingers for hours", "stays very long", "persists throughout the day"]
    }
}

price_text = {
    "Affordable": ["affordable", "cheap", "cost-effective", "not expensive", "below average"],
    "Average": ["average", "normal", "not so expensive", "not very expensive", "good", "decent"],
    "High-end": ["high-end", "expensive", "costly"]
}

# Reverse maps
rev_personality_map = build_reverse_map(personality_map)
rev_accord_map = build_reverse_map(accord_map)
rev_usage_map = build_reverse_map(usage_map)
rev_sillage_map = build_reverse_map(sillage_phrases)
rev_longevity_map = build_reverse_map(longevity_phrases)
rev_price_map = build_reverse_map(price_text)
rev_gender_map = build_reverse_map(gender_map)


# -------------------------
# normalize single entity (prioritize NOTE for accords)
# -------------------------
def normalize_entity(label, value):
    if not isinstance(value, str):
        return value

    v = value.lower().strip()

    # Nếu là NOTE
    if v in rev_note_map:
        canonical_note = rev_note_map.get(v)
        if label == "PREFERRED_ACCORD":
            accord_for_note = rev_accord_map.get(v)
            if accord_for_note:
                return {"note": canonical_note, "accord": accord_for_note}
            else:
                return {"note": canonical_note}
        else:
            return {"note": canonical_note}

    # Nếu là accord
    if v in rev_accord_map:
        accord_key = rev_accord_map.get(v)
        if label == "PREFERRED_ACCORD":
            return {"accord": accord_key}
        else:
            return {"accord": accord_key}

    # Các label khác
    if label == "PERSONALITY":
        return {"personality": rev_personality_map.get(v, value)}
    elif label == "USAGE_SITUATION":
        return {"usage": rev_usage_map.get(v, value)}
    elif label == "SILLAGE":
        val = rev_sillage_map.get(v, value)
        if isinstance(val, str) and val.lower() in ["very strong", "strong"]:
            return {"sillage": "Strong"}
        return {"sillage": val}
    elif label == "LONGEVITY":
        return {"longevity": rev_longevity_map.get(v, value)}
    elif label == "PRICE":
        return {"price": rev_price_map.get(v, value)}
    elif label == "GENDER":
        return {"gender": rev_gender_map.get(v, value)}
    else:
        return {label.lower(): value}

# -------------------------
# Helpers for ner_normalize
# -------------------------
def detect_notes_in_text(text):
    """
    Scan text and return list of detected NOTE_NAMES (canonical lower-case).
    Matches by substring (case-insensitive). Returns unique list preserving first-seen order.
    """
    if not text:
        return []
    text_low = text.lower()
    found = []
    for note in NOTE_NAMES:
        nlow = note.lower()
        if nlow in text_low and nlow not in found:
            found.append(nlow)
    return found


# -------------------------
# Normalize full profile
# -------------------------
def ner_normalize(data, note_to_idx=None, accord_to_idx=None):
    """
    Input `data` can be a dict containing keys like:
      - gender, brand, notes, preferred_accord / accords, sillage, longevity, price
      - optionally raw text in 'text' or 'raw_text' to detect notes directly
    Returns: (gender, brand, notes, accords, sillage, longevity, price)
    - notes and accords returned as lists of canonical lower-case strings
    - If note_to_idx provided, notes will be filtered to keys that exist in note_to_idx
    - If accord_to_idx provided, accords will be filtered to keys that exist in accord_to_idx
    """
    gender = str(data.get("gender", "Any")).strip() or "Any"
    brand = str(data.get("brand", "Any")).strip() or "Any"
    sillage = str(data.get("sillage", "Any")).strip() or "Any"
    longevity = str(data.get("longevity", "Any")).strip() or "Any"
    price = str(data.get("price", "Any")).strip() or "Any"

    # accords raw (could be list or comma string)
    accords_raw = data.get("preferred_accord", data.get("accords", []))
    if isinstance(accords_raw, str):
        accords_list = [x.strip().lower() for x in accords_raw.split(",") if x.strip()]
    elif isinstance(accords_raw, list):
        accords_list = [str(x).strip().lower() for x in accords_raw if str(x).strip()]
    else:
        accords_list = []

    # notes raw (could be list or comma string)
    notes_raw = data.get("notes", [])
    if isinstance(notes_raw, str):
        notes_list = [x.strip().lower() for x in notes_raw.split(",") if x.strip()]
    elif isinstance(notes_raw, list):
        notes_list = [str(x).strip().lower() for x in notes_raw if str(x).strip()]
    else:
        notes_list = []

    # If no explicit notes provided: try detect from raw text if available
    raw_text = data.get("text") or data.get("raw_text") or data.get("sentence") or ""
    if not notes_list:
        detected_notes = detect_notes_in_text(raw_text)
        if detected_notes:
            notes_list = detected_notes

    # Normalize notes_list via rev_note_map (map synonyms to canonical)
    normalized_notes = []
    for n in notes_list:
        if not isinstance(n, str):
            continue
        nl = n.lower().strip()
        # If direct match in rev_note_map -> canonical note (key)
        if nl in rev_note_map:
            can = rev_note_map.get(nl)
            normalized_notes.append(can)
        else:
            # keep as-is (fallback) - we'll later try to expand from accords
            normalized_notes.append(nl)
    # unique preserving order
    seen = set()
    notes_canonical = []
    for n in normalized_notes:
        if n not in seen:
            seen.add(n)
            notes_canonical.append(n)

    # --- Normalize accords early so we can use them to expand notes if needed ---
    accords_canonical = []
    for a in accords_list:
        if not isinstance(a, str):
            continue
        al = a.lower().strip()
        norm = normalize_entity("PREFERRED_ACCORD", al)
        ak = None
        if isinstance(norm, dict):
            accord_part = norm.get("accord")
            if accord_part and isinstance(accord_part, str):
                ak = accord_part.lower()
            else:
                accord_key = rev_accord_map.get(al, al)
                ak = accord_key.lower() if isinstance(accord_key, str) else str(accord_key)
        elif isinstance(norm, str):
            if norm in accord_map:
                ak = norm.lower()
            else:
                accord_key = rev_accord_map.get(al, al)
                ak = accord_key.lower() if isinstance(accord_key, str) else str(accord_key)
        else:
            accord_key = rev_accord_map.get(al, al)
            ak = accord_key.lower() if isinstance(accord_key, str) else str(accord_key)

        if ak and ak not in accords_canonical:
            accords_canonical.append(ak)

    if accord_to_idx:
        accords_canonical = [a for a in accords_canonical if a in accord_to_idx]

    # ------------------------------
    # NEW: If no notes found, expand conservatively (max 2 notes total)
    # ------------------------------
    MAX_ADDED = 2
    if not notes_canonical and accords_canonical:
        expanded = []
        total_added = 0

        # If there are >=2 accords, prefer to give 1 note per accord (up to MAX_ADDED)
        if len(accords_canonical) >= 2:
            for acc in accords_canonical[:2]:
                if total_added >= MAX_ADDED:
                    break
                # prefer manual map
                manual_notes = ACCORD_TO_NOTES_MANUAL.get(acc, [])
                added_one = False
                if manual_notes:
                    for cand in manual_notes:
                        cand_l = cand.lower().strip()
                        # pick the first valid canonical note (exists in note_map or NOTE_NAMES)
                        if cand_l and cand_l not in expanded:
                            if cand_l in note_map or cand_l in rev_note_map or cand_l in [n.lower() for n in NOTE_NAMES]:
                                expanded.append(cand_l)
                                total_added += 1
                                added_one = True
                                break
                    if added_one:
                        continue
                # fallback: scan accord_map synonyms and pick first matching NOTE_NAMES
                if acc in accord_map:
                    for syn in accord_map[acc]:
                        sl = syn.lower().strip()
                        # exact note name
                        if sl in note_map and sl not in expanded:
                            expanded.append(sl); total_added += 1; added_one = True; break
                        # if synonym maps to a canonical note
                        if sl in rev_note_map:
                            cand = rev_note_map.get(sl)
                            cand_l = cand.lower() if isinstance(cand, str) else str(cand).lower()
                            if cand_l not in expanded:
                                expanded.append(cand_l); total_added += 1; added_one = True; break
                        # token match
                        tokens = [t for t in sl.replace("/", " ").replace("-", " ").split() if t]
                        for note in NOTE_NAMES:
                            nlown = note.lower()
                            for t in tokens:
                                if len(t) >= 3 and t in nlown and nlown not in expanded:
                                    expanded.append(nlown); total_added += 1; added_one = True; break
                            if added_one:
                                break
                        if added_one:
                            break
                # done one accord
        else:
            # only one accord: add up to MAX_ADDED notes from manual (or fallback)
            acc = accords_canonical[0]
            manual_notes = ACCORD_TO_NOTES_MANUAL.get(acc, [])
            if manual_notes:
                for cand in manual_notes:
                    if total_added >= MAX_ADDED:
                        break
                    cand_l = cand.lower().strip()
                    if cand_l and cand_l not in expanded:
                        if cand_l in note_map or cand_l in rev_note_map or cand_l in [n.lower() for n in NOTE_NAMES]:
                            expanded.append(cand_l)
                        else:
                            expanded.append(cand_l)
                        total_added += 1
            else:
                # fallback: find candidates from accord_map synonyms
                if acc in accord_map:
                    for syn in accord_map[acc]:
                        if total_added >= MAX_ADDED:
                            break
                        sl = syn.lower().strip()
                        if sl in note_map and sl not in expanded:
                            expanded.append(sl); total_added += 1; continue
                        if sl in rev_note_map:
                            cand = rev_note_map.get(sl)
                            cand_l = cand.lower() if isinstance(cand, str) else str(cand).lower()
                            if cand_l not in expanded:
                                expanded.append(cand_l); total_added += 1; continue
                        tokens = [t for t in sl.replace("/", " ").replace("-", " ").split() if t]
                        for note in NOTE_NAMES:
                            nlown = note.lower()
                            for t in tokens:
                                if len(t) >= 3 and t in nlown and nlown not in expanded:
                                    expanded.append(nlown); total_added += 1; break
                            if total_added >= MAX_ADDED:
                                break

        # merge expanded into notes_canonical preserving uniqueness
        for n in expanded:
            if n and n not in notes_canonical:
                notes_canonical.append(n)

    # If note_to_idx provided, filter notes_canonical
    if note_to_idx:
        notes_canonical = [n for n in notes_canonical if n in note_to_idx]

    # Final de-duplication and lowercase normalization
    # ensure fully canonical lowercase and unique
    final_notes = []
    seen2 = set()
    for n in notes_canonical:
        nl = n.lower().strip()
        if nl and nl not in seen2:
            seen2.add(nl)
            final_notes.append(nl)

    notes_canonical = final_notes
    accords_canonical = [a.lower() for a in accords_canonical]

    return gender, brand, notes_canonical, accords_canonical, sillage, longevity, price