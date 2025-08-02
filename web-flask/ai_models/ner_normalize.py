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


# Mapping từ synonyms sang nhãn gốc
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

accord_map = {
    "floral": ["floral", "flowery", "flower", "blooming", "blossom", "petal-like", "bouquet"],
    "white floral": ["white floral", "delicate floral", "white flower", "soft floral", "pure bloom", "creamy flower", "jasmine-like"],
    "yellow floral": ["yellow floral", "bright floral", "colorful flower", "sunny bloom", "golden flower", "cheerful floral", "sunflower"],
    "woody": ["woody", "earthy", "wood", "tree", "bark", "cedar", "piney", "dry wood", "forest"],
    "earthy": ["earthy", "soil-like", "groundy", "damp earth", "natural", "humus", "clay"],
    "mossy": ["mossy", "green moss"],
    "citrus": ["citrus", "citrusy", "zesty", "lemony", "lime", "grapefruit", "tart", "fresh peel"],
    "sweet": ["sweet", "sugary", "candied", "chocolate", "cocoa", "caramel", "dessert-like", "syrupy"],
    "powdery": ["powdery", "soft powder"],
    "balsamic": ["balsamic", "resinous", "syrupy"],
    "amber": ["amber", "warm", "resinous"],
    "vanilla": ["vanilla", "creamy", "sweet vanilla"],
    "fruity": ["fruity", "juicy", "fruit-like"],
    "tropical": ["tropical", "island vibe", "exotic fruit", "beachy", "pineapple", "mango", "coconut"],
    "spicy": ["spicy", "peppery", "hot"],
    "warm spicy": ["warm spicy", "cozy spice", "rich spice", "cinnamon-like", "amber spice", "comforting"],
    "fresh spicy": ["fresh spicy", "zingy spice", "green spice"],
    "aromatic": ["aromatic", "herbal", "medicinal"],
    "green": ["green", "leafy", "grassy"],
    "aquatic": ["aquatic", "marine", "watery", "sea", "ocean", "fresh water"],
    "ozonic": ["ozonic", "airy", "clean", "cool breeze", "mountain air"],
    "musky": ["musky", "animalic", "skin-like"],
    "animalic": ["animalic", "feral", "musk-like"],
    "leather": ["leather", "suede", "tanned hide"],
    "smoky": ["smoky", "burnt", "charcoal", "campfire"],
    "aldehydic": ["aldehydic", "soapy", "metallic"],
    "coffee": ["coffee", "roasted", "caffeinated", "espresso", "bitter-sweet", "americano"],
    "lactonic": ["lactonic", "milky", "creamy"],
    "iris": ["iris", "powdery floral", "rooty floral", "buttery flower"],
    "violet": ["violet", "sweet floral", "purple flower", "powdery violet", "candy floral"],
    "rose": ["rose", "rosy", "romantic floral", "red flower", "velvety petal", "floral heart"],
    "tuberose": ["tuberose", "heady floral", "white bloom"],
    "lavender": ["lavender", "soothing herb", "purple herb"],
    "herbal": ["herbal", "green plant", "botanical", "plant"],
    "beeswax": ["beeswax", "waxen", "honeyed wax"],
    "honey": ["honey", "sweet nectar", "bee-sweet"],
    "whiskey": ["whiskey", "boozy", "aged alcohol", "alcohol", "liquor"],
    "cannabis": ["cannabis", "weed-like", "green narcotic"],
    "cherry": ["cherry", "red fruit", "sweet cherry", "berry"],
    "tobacco": ["tobacco", "smoked leaf", "nicotine scent", "burnt", "charcoal", "campfire"]
}

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

def normalize_entity(label, value):
    value = value.lower().strip()
    if label == "PERSONALITY":
        return rev_personality_map.get(value, value)
    elif label == "PREFERRED_ACCORD":
        return rev_accord_map.get(value, value)
    elif label == "USAGE_SITUATION":
        return rev_usage_map.get(value, value)
    elif label == "SILLAGE":
        return rev_sillage_map.get(value, value)
    elif label == "LONGEVITY":
        return rev_longevity_map.get(value, value)
    elif label == "PRICE":
        return rev_price_map.get(value, value)
    elif label == "GENDER":
        return rev_gender_map.get(value, value)
    else:
        return value  # AGE hoặc label khác không cần normalize
