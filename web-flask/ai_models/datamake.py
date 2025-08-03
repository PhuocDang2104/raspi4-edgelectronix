import pandas as pd
import random
import json
import itertools

# Load dataset
df = pd.read_csv("top_50_perfumes_dna_cleaned.csv", sep=';', encoding="utf-8")

# List từ đồng nghĩa
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
    "artistic": ["artistic", "creative", "expressive", "imaginative", "aesthetic"],
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
    "sweet": ["sweet", "sugary", "candied", "chocolate", "cocoa"],
    "powdery": ["powdery", "soft powder"],
    "balsamic": ["balsamic", "resinous", "syrupy"],
    "amber": ["amber", "warm", "resinous"],
    "vanilla": ["vanilla", "creamy", "sweet vanilla"],
    "fruity": ["fruity", "juicy", "fruit-like"],
    "tropical": ["tropical", "island vibe", "exotic fruit", "beachy", "pineapple", "mango", "coconut"],
    "spicy": ["spicy", "peppery", "hot", "peppery"],
    "warm spicy": ["warm spicy", "cozy spice", "rich spice", "cinnamon-like", "amber spice", "comforting"],
    "fresh spicy": ["fresh spicy", "zingy spice", "green spice"],
    "aromatic": ["aromatic", "herbal", "medicinal"],
    "green": ["green", "leafy", "grassy"],
    "aquatic": ["aquatic", "marine", "watery", "sea", "ocean", "fresh water"],
    "ozonic": ["ozonic", "airy", "clean", "cool breeze", "mountain air"],
    "musky": ["musky", "animalic", "skin-like"],
    "animalic": ["animalic", "feral", "musk-like"],
    "leather": ["leather", "suede", "tanned hide"],
    "smoky": ["smoky", "burnt", "charcoal"],
    "aldehydic": ["aldehydic", "soapy", "metallic"],
    "coffee": ["coffee", "roasted", "caffeinated","espresso", "bitter-sweet", "americano"],
    "sweet": ["sweet", "sugary", "candied", "caramel", "dessert-like", "syrupy"],
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

# Usage & attributes mapping
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
        "noun": [
            "light sillage",
            "a subtle trail",
            "soft projection",
            "soft sillage",
            "a faint scent trail",
            "a barely noticeable presence"
        ],
        "verb": [
            "has a soft trail",
            "projects subtly",
            "leaves a soft trail",
            "is barely noticeable",
            "fades quickly into the background"
        ]
    },
    "Medium": {
        "noun": [
            "medium sillage",
            "moderate sillage",
            "balanced projection",
            "a decent scent trail",
            "a noticeable but not overwhelming trail",
            "medium presence"
        ],
        "verb": [
            "projects moderately",
            "leaves a balanced trail",
            "is noticeable but not overwhelming",
            "lingers with decent strength"
        ]
    },
    "Strong": {
        "noun": [
            "strong sillage",
            "a powerful scent trail",
            "bold projection",
            "a lingering presence",
            "a prominent scent",
            "dense sillage"
        ],
        "verb": [
            "projects boldly",
            "leaves a powerful scent trail",
            "fills the air with a noticeable presence",
            "is strong and persistent"
        ]
    },
    "Very Strong": {
        "noun": [
            "very strong sillage",
            "an intense scent trail",
            "overpowering projection",
            "a room-filling aroma",
            "a room-filling projection",
            "a room-filling sillage",
            "an extremely dense sillage"
        ],
        "verb": [
            "fills the room instantly",
            "projects intensely",
            "overpowers the surroundings",
            "is extremely strong and room-filling"
        ]
    }
}


longevity_phrases = {
    "Short": {
        "noun": [
            "short longevity",
            "quick fade",
            "brief lasting power",
            "light staying power",
            "low durability"
        ],
        "verb": [
            "fades quickly",
            "doesn't last long",
            "wears off soon",
            "loses scent fast"
        ]
    },
    "Medium": {
        "noun": [
            "medium longevity",
            "moderate staying power",
            "a decent wear time",
            "balanced longevity",
            "noticeable duration"
        ],
        "verb": [
            "doesn't fade so quickly",
            "lasts a decent time",
            "stays on fairly well",
            "lingers moderately",
            "holds through a few hours"
        ]
    },
    "Long": {
        "noun": [
            "long longevity",
            "good longevity",
            "long-lasting scent",
            "strong longevity",
            "all-day wear",
            "extended staying power",
            "persistent performance"
        ],
        "verb": [
            "lasts all day",
            "lasts long",
            "lasts very long",
            "lasts extremely long",
            "lingers for hours",
            "stays very long",
            "persists throughout the day"
        ]
    }
}

price_text = {
    "Affordable": ["affordable", "cheap", "cost-effective", "not expensive", "below average"],
    "Average": ["average", "normal", "not so expensive", "not very expensive", "good", "decent"],
    "High-end": ["high-end", "expensive", "costly"]
}

# Các mẫu template câu
sentence_templates_noun = [
    "I'm a {age} years old {gender} with a {personality} style I enjoy {accord} scents and wear them {usage} I prefer a perfume that has {longevity} and {price} fragrances",
    "As a {age}-year-old {gender} I love {accord} scents that suit my {personality} side especially {usage} My choice is usually anything that has {sillage} {longevity} and {price}",
    "{gender_cap} {age} prefers {accord} notes and a {personality} personality These perfumes are worn {usage} with something has {sillage} {longevity} and {price} in mind",
    "Being a {age}-year-old {gender} I lean toward {accord} fragrances reflecting my {personality} vibe I use them {usage} I like {sillage} {longevity} and {price} options",
    "At {age} being a {gender} I usually wear {accord} perfumes that reflect my {personality} side I wear them {usage} and I like scents with {sillage} {longevity} and are {price}",
    "As a {gender} of {age} I prefer {accord} fragrances that fit my {personality} vibe They're great {usage} and I always go for a {longevity} and a {price} picks And additionally about sillage something that has {sillage}",
    "I'm {age} years old and a {gender} I like {accord} scents that match my {personality} personality I use them mostly {usage} and prefer something that {sillage} and {price} ones",
    "Being a {personality} {gender} aged {age} I gravitate toward {accord} fragrances They're ideal {usage} with a {sillage} {longevity} and usually quite {price}",
    "At {age} my go-to scents as a {gender} are {accord} They go well with my {personality} style I wear them {usage} and enjoy a {longevity} a {sillage} and {price} perfumes",
    "As a {gender} age {age} I adore {accord} perfumes for my {personality} side I often wear them {usage} My preferences include {longevity} {sillage} and {price}",
    "I'm a {age} {gender} I want a {accord} accord {usage} with girl friend I want a perfume that has a {longevity} with {sillage} It should be {price}",
    "I'm {age} and identify as {gender} My {personality} vibe matches perfectly with a {accord} scents I wear them {usage} and look for something that is {sillage} and {price} options",
    "You could say I'm a {age}-year-old {gender} who loves {accord} perfumes that show my {personality} personality Perfect {usage} and I stick with {sillage} {longevity} and {price} ones",
    "Hey I'm {age} and a {gender} I usually go for {accord} scents that vibe with my {personality} side I wear them {usage} and like them when they have {longevity} and {price}",
    "So yeah I'm a {gender} {age} years old I really enjoy {accord} fragrances—they fit my {personality} style I use them mostly {usage} and prefer {sillage} {longevity} and {price} ones",
    "Honestly {accord} scents are my thing I'm {age} a {gender} and kinda {personality} I wear them {usage} and I like them to have a {sillage} a {longevity} and be {price}",
    "I'm {age} and a {gender} and I totally go for {accord} perfumes They match my {personality} vibe Usually wear them {usage} and yeah {longevity} {sillage} and {price} matter to me",
    "Well being a {personality} {gender} aged {age} I just love {accord} scents I mostly wear them {usage} Give me that {sillage} {longevity} and {price} combo please",
    "I'm all about {accord} fragrances I'm {age} {gender} with a {personality} personality They're great {usage} and I always go for {sillage} {longevity} and {price}",
    "I'm a {age}-year-old {gender} pretty {personality} and totally into {accord} scents I wear them {usage} and like them {sillage} {longevity} and {price}",
    "For me {accord} perfumes will work I'm {gender} {age} and kinda {personality} I rock them {usage} and always pick {sillage} and {price} ones",
    "I'm {age} a {gender} and into {accord} notes They match my {personality} energy and I mostly wear them {usage} I prefer {sillage} a {longevity} and {price} perfumes",
    "You know as a {gender} who's {age} I love {accord} perfumes that feel really {personality} I wear them {usage} and I like scents with {sillage} a {longevity} and that are {price}",
    "Being a {gender} I think {accord} scents really bring out my {personality} side I'm {age} usually wear them {usage} and love them {sillage} {longevity} and {price}",
    "Honestly {accord} scents just click with me I'm a {personality} {gender} age {age} and I use them {usage} I prefer a {sillage} {longevity} and {price}",
    "At {age} as a {gender} I lean toward {accord} perfumes—they really suit my {personality} personality I like wearing them {usage} with a {sillage} a {longevity} and {price}",
    "Yeah I'm a {age} year old {gender} who's into {accord} perfumes They're great for my {personality} side I wear them {usage} and go for {longevity} {sillage} and {price}",
    "To be honest {accord} scents are just perfect for my {personality} side I'm a {gender} {age} and wear them mostly {usage} I like them {sillage} and {price} Oh yeah and something must be {longevity}",
    "I'm {age} I am {gender} that has a {personality} style I enjoy {accord} scents and I intend to wear them {usage} For longevity I prefer fragrance that is {longevity} And sillage i would like something has {sillage} And yeah something that must be {price} in price",
    "I am {gender} about {age} years old I think that I'm a person I use them mostly {usage} Something that is {price} About longevity i think i'll go for {longevity} maybe {sillage} for sillage",
    "I'm a {age} {gender} I think that i'm kinda a {personality} person My favourite recently has been {accord} I also wanna try some {accord_sub} scent as well The sillage and longevity must be {sillage} & {longevity} I'm into something that is {price} in terms of price",
    "I'm a {age} My favorite accord is {accord} I would prefer something has a {sillage} and a {longevity} Something that i can use {usage}",
    "I'm {age} I would describe myself as {personality} I would prefer something has a {sillage} with {longevity} Something that i can use {usage}",
    "I'm {gender} I would describe myself a {personality} person I would like something has {longevity} and {sillage} Something that i can use {usage} And the perfume must be {price} also",
    "I'm a {gender} {age} you can say that I'm {personality} A perfume that must has {sillage} and {longevity} I will use it for {usage} It should be {price} as well",
    "I'm a {age} My favorite accord is {accord} I would prefer something has {sillage} and {longevity} Something that i can use {usage}",
    "I'm a {age} years old {gender} You can say that I'm a {personality} person I would like to use the perfume for {usage}",
    "I'm kinda into an accord that smell like ocean I would go for something that has {sillage} and a {longevity} Must be {price} also I will use it for {usage}",
    "So I'm {gender} looking for an accord that fits my {personality} vibe It should has a {sillage} I need it for {usage}",
    "So I'm a {gender} about {age} trying to find a scent that matches my {personality} energy It should has a {longevity} I'm gonna use it for {usage}",
    "I'm looking for something that smell like {accord} or {accord_sub} A perfume for {gender} by the way I like it having {longevity} {sillage} and {price} It's for {usage}",
    "I'm {age} I'm a {gender} I'm kinda {personality} I'm using it for {usage} the perfume must have {sillage} and It should be {price} Would be nice if it has {accord} scent"
]


sentence_templates_verb = [
    "I'm a {age}-year-old {gender} with a {personality} style I enjoy {accord} scents and wear them {usage} I prefer something that {longevity} and {sillage}",
    "As a {gender} who's {age} my {personality} vibe fits with {accord} fragrances I wear them {usage} and like a perfume with a sillage that {sillage} and longevity that {longevity}",
    "{gender_cap} age {age} with a {personality} personality I use {accord} scents mostly {usage} and want a perfume that {longevity} {sillage} and is {price}",
    "I'm {age} and a {gender} My signature scents are {accord} types which I wear {usage} I want a perfume that {sillage} {longevity} and stays within a {price} range",
    "As a {gender} of {age} I'm all about {accord} notes for my {personality} personality I use them {usage} and prefer something that {longevity} {sillage} and feels {price}",
    "Being {age} {gender} and {personality} I prefer {accord} accords I often use them {usage} I go for perfumes that {longevity} and {sillage} and that are {price}",
    "I'm a {gender} {age} I like {accord} scents and want a perfume that {longevity} {sillage} and isn't too {price} I'll wear it mostly {usage}",
    "Hey I'm {age} and identify as {gender} I'm into {accord} perfumes that I wear {usage} Ideally something that {sillage} and stays {price}",
    "So I'm a {gender} {age} years old with a {personality} personality I like {accord} scents I can use {usage} I want a fragrance with a sillage that {sillage} and which {longevity} and is {price}",
    "I prefer {accord} fragrances for my {personality} vibe I'm {age} a {gender} and I wear perfume {usage} I look for scents that {longevity} and are {price}",
    "My name's not important but I'm a {gender} age {age} quite {personality} I go for {accord} scents used {usage} and I like when they {longevity} and {sillage}",
    "Honestly I'm a {age}-year-old {gender} and I wear {accord} perfumes to match my {personality} side I prefer fragrances that {longevity} and are {price}",
    "I'm {age} a {gender} My go-to perfumes {longevity} {sillage} and go well with {accord} notes I usually wear them {usage} and prefer {price} options",
    "So I'm {gender} and {age} With a {personality} taste I enjoy {accord} fragrances {usage} My favorites are ones that {longevity} and are {price}",
    "Hey there I'm a {age} {gender} I'm quite {personality} I love {accord} perfumes that I can wear {usage} I want something that {longevity} and {sillage} It should be {price}",
    "I'm {age} and a {gender} I usually go for {accord} fragrances For {usage} I want something that {longevity} and {sillage} not too {price}",
    "I'm {gender} around {age} kinda {personality} I'd love a perfume with {accord} notes something I can wear {usage} It needs to {longevity} {sillage} and be {price}",
    "For me perfumes that {longevity} and {sillage} are perfect I'm a {gender} {age} and into {accord} scents I wear them {usage} and want something that feels {price}",
    "You know I'm {age} a {gender} and pretty {personality} I use {accord} scents for {usage} and I need them to {longevity} {sillage} and be {price}",
    "Perfumes that {longevity} and {sillage} are must-haves for me I'm a {gender} age {age} and enjoy {accord} fragrances I usually wear them {usage} and prefer {price} options",
    "I'm {age} and a {gender} I think of myself as {personality} and I like {accord} perfumes that I use {usage} The scent must {longevity} and {sillage} and not be too {price}",
    "To me a fragrance that {longevity} and {sillage} is essential I'm {age} {gender} kind of {personality} and love {accord} notes I wear them mostly {usage}",
    "Hi I'm a {age} {gender} I'm really into {accord} accords I'd prefer something that {longevity} and {sillage} I use it mostly {usage} {price} is also a factor",
    "I'm a {gender} with a {personality} vibe aged {age} I like wearing {accord} perfumes {usage} Ideally the fragrance should {sillage} {longevity} and be {price}",
    "I'm {age} I love {accord} scents I'm {gender} kinda {personality} and I wear them {usage} I look for something that {longevity} {sillage} and is {price}",
    "So I'm a {gender} {age} with a {personality} personality I like to use {accord} fragrances {usage} especially those that {longevity} and {sillage} They should be {price}",
    "I would like a scent that {longevity} and {sillage} I'm {age} a {gender} and into {accord} notes I plan to use it mostly {usage} and prefer something {price}",
    "Give me something that {longevity} {sillage} and I'm happy I'm a {gender} {age} pretty {personality} and prefer {accord} scents to wear {usage} {price} is ideal",
    "At {age} as a {gender} I feel like {accord} fragrances really bring out my {personality} I use them mostly {usage} and I go for perfumes that {sillage} and {longevity}",
    "Being a {gender} in my {age}s I gravitate toward {accord} scents that give off that {personality} vibe I use them mostly {usage} and I like perfumes that {sillage} and {longevity}",
    "For me being {age} and {gender} {accord} perfumes just click I'm into that whole {personality} feel I usually wear them {usage} and love when the scent {longevity} and {sillage}"
]



TRAIN_DATA = []
skipped = 0

template_cycle_noun = itertools.cycle(sentence_templates_noun)
template_cycle_verb = itertools.cycle(sentence_templates_verb)
accord_cycle = itertools.cycle(list(accord_map.keys()))

for idx, row in df.iterrows():
    for _ in range(2000):  # tạo 2000 câu cho mỗi dòng 
        age = random.randint(18, 65)

        gender_raw = row.get("gender", "unisex").lower()
        gender_synonyms = gender_map.get(gender_raw, [gender_raw])
        gender = random.choice(gender_synonyms)
        gender = gender.capitalize()

        personality_base = random.choice(list(personality_map.keys())) # chọn random các personality

        accord_base = next(accord_cycle)

        usage_key = random.choice(list(usage_map.keys()))  # Chọn 1 trong 10 usage chính
        usage = random.choice(usage_map[usage_key])
        sillage = random.choice(["Light","Medium","Strong","Very Strong"])
        longevity = random.choice(["Short", "Medium", "Long"])
        price = random.choice(["High-end", "Affordable", "Average"])

        # Chọn synonym nếu có
        personality = random.choice(personality_map.get(personality_base, [personality_base]))
        accord = random.choice(accord_map.get(accord_base, [accord_base]))
        accord_sub = random.choice(accord_map.get(accord_base, [accord_base]))

        usage_phrase = usage

        sillage_noun = random.choice(sillage_phrases[sillage]["noun"])
        sillage_verb = random.choice(sillage_phrases[sillage]["verb"])

        longevity_noun = random.choice(longevity_phrases[longevity]["noun"])
        longevity_verb = random.choice(longevity_phrases[longevity]["verb"])
        
        price_phrase = random.choice(price_text[price])


        

        
        # Chọn random xem câu này dùng template nào
        template_type = random.choice(["noun", "verb"])

        if template_type == "noun":
            template = next(template_cycle_noun)
            sentence = template.format(
                age=age,
                gender=gender.lower(),
                gender_cap=gender,
                personality=personality,
                accord=accord,
                accord_sub=accord_sub,
                usage=usage_phrase,
                sillage=sillage_noun,
                longevity=longevity_noun,
                price=price_phrase
            )
        else:
            template = next(template_cycle_verb)
            sentence = template.format(
                age=age,
                gender=gender.lower(),
                gender_cap=gender,
                personality=personality,
                accord=accord,
                accord_sub=accord_sub,
                usage=usage_phrase,
                sillage=sillage_verb,
                longevity=longevity_verb,
                price=price_phrase
            )

        # Xác định vị trí các entity trong câu
        ents = []

        def try_find(phrase, label):
            try:
                start = sentence.index(phrase)
                end = start + len(phrase)
                ents.append((start, end, label))
            except ValueError:
                pass  # Không thêm nếu không tìm thấy

        def try_find_lower(phrase, label):
            try:
                start = sentence.lower().index(phrase.lower())
                end = start + len(phrase)
                ents.append((start, end, label))
            except ValueError:
                pass

        # Thử tìm từng entity, nếu không có thì bỏ qua
        try_find(str(age), "AGE")
        try_find_lower(gender, "GENDER")
        try_find_lower(personality, "PERSONALITY")
        try_find_lower(accord, "PREFERRED_ACCORD")
        try_find_lower(accord_sub, "PREFERRED_ACCORD")
        try_find(usage_phrase, "USAGE_SITUATION")
        try_find(sillage_noun, "SILLAGE")
        try_find(sillage_verb, "SILLAGE")
        try_find(longevity_noun, "LONGEVITY")
        try_find(longevity_verb, "LONGEVITY")   
        try_find(price_phrase, "PRICE")

        # Chỉ thêm nếu có ít nhất 1 entity
        if ents:
            TRAIN_DATA.append((sentence, {"entities": ents}))
        else:
            skipped += 1

# In ra thử kết quả
print(f"\n Generated {len(TRAIN_DATA)} synthetic NER training samples.")
print(f" Skipped {skipped} samples due to matching error.\n")

for i, (text, annotation) in enumerate(TRAIN_DATA[:5]):
    print(f"Sample {i+1}:")
    print("Text:", text)
    print("Entities:", annotation["entities"])
    print("-" * 80)

with open("ner_training_data.json", "w", encoding="utf-8") as f:
    json.dump(TRAIN_DATA, f, ensure_ascii=False, indent=2)

