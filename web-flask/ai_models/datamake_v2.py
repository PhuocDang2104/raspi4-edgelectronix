import pandas as pd
import random
import json
import itertools
import re

# ------------------
# datamake.py (FINAL corrected)
# - Distinguish ACCORDS and NOTES using provided lists
# - Use the full template sets and synonyms you provided
# - If a customer mentions an accord, automatically pick related notes
# - If a customer mentions notes, map them back to related accords
# - Templates include: full noun/verb templates + "known accords/notes/mixed" templates
# - Uses case-insensitive multi-match annotation via re.finditer
#
# Run: python datamake.py
# Output: ner_training_data.json
# ------------------

# Load dataset (same CSV as before)
df = pd.read_csv("top_50_perfumes_dna_cleaned.csv", sep=';', encoding="utf-8")

# ---------- Provided lists (user-specified) ----------
ACCORD_NAMES = [
    "aldehydic","amber","animalic","aquatic","aromatic","balsamic","beeswax","cannabis",
    "cherry","chocolate","citrus","coconut","coffee","earthy","floral","fresh",
    "fresh spicy","fruity","green","herbal","honey","iris","lactonic","lavender",
    "leather","mossy","musky","ozonic","powdery","rose","smoky","sweet","tobacco",
    "tropical","tuberose","vanilla","violet","warm spicy","whiskey","white floral",
    "woody","yellow floral"
]

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

# ---------- Accord synonyms mapping (from your accord_map) ----------
accord_map = {
    "floral": ["floral", "flowery", "flower", "blooming", "blossom", "petal-like", "bouquet"],
    "white floral": ["white floral", "delicate floral", "white flower", "soft floral", "pure bloom", "creamy flower", "jasmine-like"],
    "yellow floral": ["yellow floral", "bright floral", "colorful flower", "sunny bloom", "golden flower", "cheerful floral", "sunflower"],
    "woody": ["woody", "oak", "wood", "tree", "bark", "cedar", "piney", "dry wood", "forest", "pine tree"],
    "earthy": ["earthy", "soil-like", "groundy", "damp earth", "natural", "humus", "clay", "soil"],
    "mossy": ["mossy", "green moss"],
    "citrus": ["citrus", "citrusy", "zesty", "lemony", "lime", "grapefruit", "tart", "fresh peel", "bitter orange", "blood orange", "clementine", "mandarin orange", "orange"],
    "sweet": ["sweet", "sugary", "candied", "chocolate",  "dark chocolate", "cocoa", "whipped cream", "dessert-like", "syrupy", "salted caramel","caramel"],
    "powdery": ["powdery", "soft powder"],
    "balsamic": ["balsamic", "resinous", "syrupy"],
    "amber": ["amber", "warm", "resinous"],
    "vanilla": ["vanilla", "creamy", "sweet vanilla"],
    "fruity": ["fruity", "juicy", "fruit-like"],
    "tropical": ["tropical", "island vibe", "exotic fruit", "beachy", "pineapple", "mango", "coconut"],
    "spicy": ["spicy", "peppery", "hot", "peppery", "ginger", "ginger flower", "ceylon cinnamon", "saffron"],
    "warm spicy": ["warm spicy", "cozy spice", "rich spice", "cinnamon-like", "amber spice", "comforting", "cinnamon"],
    "fresh spicy": ["fresh spicy", "zingy spice", "green spice"],
    "aromatic": ["aromatic", "herbal", "medicinal"],
    "green": ["green", "leafy", "grassy"],
    "aquatic": ["aquatic", "marine", "watery", "sea", "ocean", "fresh water"],
    "ozonic": ["ozonic", "airy", "clean", "cool breeze", "mountain air", "clean breeze"],
    "musky": ["musky", "animalic", "skin-like"],
    "animalic": ["animalic", "feral", "musk-like"],
    "leather": ["leather", "suede", "tanned hide"],
    "smoky": ["smoky", "burnt", "charcoal", "campfire", "smoky tobacco"],
    "aldehydic": ["aldehydic", "soapy", "metallic", "soap"],
    "coffee": ["coffee", "roasted", "caffeinated","espresso", "bitter-sweet", "americano", "roasted coffee"],
    "lactonic": ["lactonic", "milky", "creamy"],
    "iris": ["iris", "powdery floral", "rooty floral", "buttery flower"],
    "violet": ["violet", "sweet floral", "purple flower", "powdery violet", "candy floral"],
    "rose": ["rose", "rosy", "romantic floral", "red flower", "velvety petal", "floral heart"],
    "tuberose": ["tuberose", "heady floral", "white bloom"],
    "lavender": ["lavender", "soothing herb", "purple herb"],
    "herbal": ["herbal", "green plant", "botanical", "plant"],
    "beeswax": ["beeswax", "waxen", "honeyed wax"],
    "honey": ["honey", "sweet nectar", "bee-sweet"],
    "whiskey": ["whiskey", "boozy", "aged alcohol", "alcohol", "liquor", "brandy"],
    "cannabis": ["cannabis", "weed-like", "green narcotic"],
    "cherry": ["cherry", "red fruit", "sweet cherry", "berry"],
    "tobacco": ["tobacco", "smoked leaf", "nicotine scent", "burnt", "charcoal", "campfire", "cigarette"]
}

# ---------- Helper: note -> accord mapping (seeded + keyword rules) ----------
def norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

note_to_accords = {}
for note in NOTE_NAMES:
    note_norm = norm(note)
    matched = set()
    for accord in ACCORD_NAMES:
        if accord in note_norm:
            matched.add(accord)
    note_to_accords[note] = matched

# keyword-based rules (extended)
keyword_map = {
    'citrus': ['bergamot', 'lemon', 'lime', 'grapefruit', 'clementine', 'tangerine', 'mandarin', 'orange', 'bitter orange', 'calabrian bergamot', 'amalfi lemon', 'green mandarin', 'mandarin orange', 'citruses'],
    'vanilla': ['vanilla', 'madagascar vanilla', 'tahitian vanilla', 'vanille'],
    'floral': ['jasmine','rose','lily','gardenia','tuberose','y lang','ylang','magnolia','peony','may rose','casablanca','jasmine sambac','narcissus','hyacinth','heliotrope','orange blossom','lily-of-the-valley','lotus','grasse rose','turkish rose','tunisian neroli','silkwood blossom'],
    'woody': ['sandalwood','cedar','oakmoss','vetiver','cashmeran','cashmere','texas cedar','virginia cedar','woodsy','woody'],
    'spicy': ['cinnamon','clove','nutmeg','cardamom','saffron','ginger','black pepper','pink pepper','pepper','ceylon cinnamon'],
    'sweet': ['sugar','caramel','honey','whipped cream','syrup','candy','syrupy','salted caramel'],
    'coffee': ['coffee','espresso','roasted coffee'],
    'chocolate': ['chocolate','cocoa','dark chocolate'],
    'tobacco': ['tobacco','tobacco leaf','rum','whiskey'],
    'aquatic': ['calone','marine','sea','ocean','aquatic','fresh water'],
    'mossy': ['moss','oakmoss','mossy'],
    'musky': ['musk','musk-like','white musk'],
    'herbal': ['basil','sage','rosemary','mint','thyme','oregano','laurels','artemisia','water mint'],
    'fruity': ['apple','apricot','peach','plum','pear','pineapple','mango','passionfruit','raspberry','red berries','red currant','red fruits','strawberry','big strawberry','litchi'],
    'smoky': ['birch','incense','smoky','myrrh','charcoal','smoked','cigar'],
    'amber': ['amber','ambergris','ambroxan','black amber'],
    'beeswax': ['beeswax','bees wax'],
    'leather': ['leather','suede']
}

for note in NOTE_NAMES:
    if not note_to_accords.get(note):
        n = norm(note)
        matched = set()
        for accord, keywords in keyword_map.items():
            for kw in keywords:
                if kw in n:
                    if accord in ACCORD_NAMES:
                        matched.add(accord)
                    else:
                        # fallback mapping
                        if accord == 'spicy':
                            matched.add('spicy')
                        elif accord == 'sweet':
                            matched.add('sweet')
                        elif accord == 'fruity':
                            matched.add('fruity')
                        elif accord == 'woody':
                            matched.add('woody')
                        elif accord == 'vanilla':
                            matched.add('vanilla')
                        elif accord == 'amber':
                            matched.add('amber')
                        elif accord == 'aquatic':
                            matched.add('aquatic')
                        elif accord == 'mossy':
                            matched.add('mossy')
                        elif accord == 'musky':
                            matched.add('musky')
                        elif accord == 'herbal':
                            matched.add('aromatic')
                        else:
                            matched.add(accord)
                    break
        note_to_accords[note] = matched

# invert mapping: accord -> notes list
accord_to_notes = {a:set() for a in ACCORD_NAMES}
for note, accords in note_to_accords.items():
    for a in accords:
        accord_to_notes.setdefault(a, set()).add(note)

for a in accord_to_notes:
    accord_to_notes[a] = sorted(list(accord_to_notes[a]))

# ---------- Synonyms (extended) ----------
gender_map = {
    "men": ["man", "boy", "male", "gentleman", "guy", "males"],
    "women": ["woman", "girl", "female", "lady", "ladies"],
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

# usage, sillage, longevity, price (full phrases retained)
usage_map = {
    "Work": [
        "for work","at the office","during working hours","in professional settings","for business-related occasions","when i go to work","when i am at the office","when i work","when i have work","when i am working","when i am in a meeting","when i am collaborating with my co-workers","when i need to concentrate"],
    "Casual": ["for casual outings","on relaxed days","for informal hangouts","during laid-back times","when dressing down","for daily","on normal days","for everyday occasions","when i want to feel comfortable","when i am going out casually"],
    "Date Night": ["for a romantic night out","on a date night","for romantic occasions","during intimate evenings","for date nights","when going out with someone special","for dating","on a date","when i go on a date","when i have a date","when i am on a date","when i go on a date night","when i have a date night","when i am on a date night"],
    "Formal": ["for formal events","at formal gatherings","during elegant occasions","for black-tie events","in ceremonial settings","for formal party","when attending formal events","for formal occasion","when i go to formal party","when i attend formal events"],
    "Everyday": ["for daily wear","on a regular basis","for everyday use","as a go-to scent","for routine days","on a daily basis","normal days"],
    "Gym": ["at the gym","while working out","during fitness sessions","in exercise routines","when staying active","when i go to the gym","when i hit the gym","when i work out","while hitting the gym","when hitting the gym"],
    "Vacation": ["while traveling","on vacation","during trips","for getaways","on holidays","when i travel","on beach days"],
    "Outdoor Activities": ["for outdoor activities","while being active outside","during nature adventures","for hiking","on hikes or walks","in open-air events","for activities","when playing sports","for playing sports","when playing sports","for playing basketball","for playing football","for tennis","for outdoor stuff","on picnic days","for barbecues","for outdoor gatherings","for nature exploration"],
    "Party": ["at parties","for party","at party","for parties","when clubbing","during nightlife","on nights out","for dancing events","for partying","for clubbing","when i go to party","for club nights"],
    "Relaxing at Home": ["when relaxing at home","during downtime","on lazy days","in cozy moments","while staying in","in cozy nights"]
}

sillage_phrases = {
    "Light": {"noun": ["light sillage","a subtle trail","soft projection","soft sillage","a faint scent trail","a barely noticeable presence"], "verb": ["has a soft trail","projects subtly","leaves a soft trail","is barely noticeable","fades quickly into the background"]},
    "Medium": {"noun": ["medium sillage","moderate sillage","balanced projection","a decent scent trail","a noticeable but not overwhelming trail","medium presence"], "verb": ["projects moderately","leaves a balanced trail","is noticeable but not overwhelming","lingers with decent strength"]},
    "Strong": {"noun": ["strong sillage","a powerful scent trail","bold projection","a lingering presence","a prominent scent","dense sillage"], "verb": ["projects boldly","leaves a powerful scent trail","fills the air with a noticeable presence","is strong and persistent"]},
    "Very Strong": {"noun": ["very strong sillage","an intense scent trail","overpowering projection","a room-filling aroma","a room-filling projection","a room-filling sillage","an extremely dense sillage"], "verb": ["fills the room instantly","projects intensely","overpowers the surroundings","is extremely strong and room-filling"]}
}

longevity_phrases = {
    "Short": {"noun": ["short longevity","quick fade","brief lasting power","light staying power","low durability"], "verb": ["fades quickly","doesn't last long","wears off soon","loses scent fast"]},
    "Medium": {"noun": ["medium longevity","moderate staying power","a decent wear time","balanced longevity","noticeable duration"], "verb": ["doesn't fade so quickly","lasts a decent time","stays on fairly well","lingers moderately","holds through a few hours"]},
    "Long": {"noun": ["long longevity","good longevity","long-lasting scent","strong longevity","all-day wear","extended staying power","persistent performance"], "verb": ["lasts all day","lasts long","lasts very long","lasts extremely long","lingers for hours","stays very long","persists throughout the day","sticks around for hours","sticks around for a long time"]}
}

price_text = {"Affordable": ["affordable","cheap","cost-effective","not expensive","below average"], "Average": ["average","normal","not so expensive","not very expensive","good","decent"], "High-end": ["high-end","expensive","costly"]}

# ---------- Templates (both the long noun/verb set and the known accord/note/mixed set) ----------
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

# Also keep explicit "known" templates to represent customer who knows accords/notes
sentence_templates_known_accords = [
    "I'm a {age} {gender} and I like {accords} scents for {usage}",
    "I prefer {accords} perfumes, especially for {usage}",
    "{gender_cap} age {age} usually wears {accords} notes when {usage}"
]

sentence_templates_known_notes = [
    "I'm {age} and I enjoy notes like {notes} for {usage}",
    "I love {notes} in a fragrance — they work well for {usage}",
    "{gender_cap} age {age} prefers perfumes with notes such as {notes} when {usage}"
]

sentence_templates_mixed = [
    "I like {accords} scents, especially with notes like {notes} for {usage}",
    "As a {personality} {gender}, I want {accords} with notes like {notes} for {usage}"
]

# cycles
template_cycle_noun = itertools.cycle(sentence_templates_noun)
template_cycle_verb = itertools.cycle(sentence_templates_verb)
known_acc_cycle = itertools.cycle(sentence_templates_known_accords)
known_note_cycle = itertools.cycle(sentence_templates_known_notes)
mixed_cycle = itertools.cycle(sentence_templates_mixed)

TRAIN_DATA = []
skipped = 0

# find helper
def find_all_occurrences(text, phrase):
    matches = []
    if not phrase:
        return matches
    for m in re.finditer(re.escape(phrase), text, flags=re.IGNORECASE):
        matches.append((m.start(), m.end()))
    return matches

# main generation loop (merged behavior)
for idx, row in df.iterrows():
    for _ in range(2000):
        age = random.randint(18, 65)
        gender_raw = str(row.get("gender", "unisex")).lower()
        gender_synonyms = gender_map.get(gender_raw, [gender_raw])
        gender_choice = random.choice(gender_synonyms)
        gender = gender_choice
        gender_cap = gender_choice.capitalize()
        personality_base = random.choice(list(personality_map.keys()))
        personality = random.choice(personality_map.get(personality_base, [personality_base]))

        sample_mode = random.choices(["accords","notes","mixed"], weights=[0.5,0.3,0.2])[0]

        usage_key = random.choice(list(usage_map.keys()))
        usage = random.choice(usage_map[usage_key])
        sillage = random.choice(["Light","Medium","Strong","Very Strong"])
        longevity = random.choice(["Short","Medium","Long"])
        price = random.choice(["High-end","Affordable","Average"])

        sillage_noun = random.choice(sillage_phrases[sillage]["noun"])
        sillage_verb = random.choice(sillage_phrases[sillage]["verb"])
        longevity_noun = random.choice(longevity_phrases[longevity]["noun"])
        longevity_verb = random.choice(longevity_phrases[longevity]["verb"])
        price_phrase = random.choice(price_text[price])

        accords_selected = []
        notes_selected = []

        if sample_mode == 'accords':
            num_accords = random.choices([1,2,3], weights=[0.7,0.25,0.05])[0]
            accords_selected = random.sample(ACCORD_NAMES, k=num_accords)
            # pick notes from these accords
            notes_pool = []
            for a in accords_selected:
                pool = accord_to_notes.get(a, [])
                if pool:
                    k = 1 if len(pool)==1 else random.choice([1,1,2])
                    notes_pool.extend(random.sample(pool, k=min(k, len(pool))))
            notes_selected = list(dict.fromkeys(notes_pool))[:4]
            # choose template style: old noun/verb (single accord) or known_acc (multi)
            if random.random() < 0.4:
                # use noun/verb templates (pick single accord)
                chosen_accord = random.choice(accords_selected)
                if random.random() < 0.5:
                    template = next(template_cycle_noun)
                else:
                    template = next(template_cycle_verb)
                sentence = template.format(age=age, gender=gender.lower(), gender_cap=gender_cap, personality=personality, accord=chosen_accord, accord_sub=chosen_accord, usage=usage, sillage=sillage_noun, longevity=longevity_noun, price=price_phrase)
            else:
                template = next(known_acc_cycle)
                sentence = template.format(age=age, gender=gender.lower(), gender_cap=gender_cap, accords=", ".join(accords_selected), usage=usage)

        elif sample_mode == 'notes':
            num_notes = random.choices([1,2,3,4], weights=[0.5,0.3,0.15,0.05])[0]
            notes_selected = random.sample(NOTE_NAMES, k=num_notes)
            inferred_accords = set()
            for n in notes_selected:
                inferred_accords.update(note_to_accords.get(n, set()))
            accords_selected = sorted(list(inferred_accords))[:3]
            # choose between known_note templates or noun/verb fallback
            if random.random() < 0.6:
                template = next(known_note_cycle)
                sentence = template.format(age=age, gender=gender.lower(), gender_cap=gender_cap, notes=", ".join(notes_selected), usage=usage)
            else:
                # use noun/verb template with first inferred accord as {accord}
                chosen_accord = accords_selected[0] if accords_selected else random.choice(ACCORD_NAMES)
                if random.random() < 0.5:
                    template = next(template_cycle_noun)
                else:
                    template = next(template_cycle_verb)
                sentence = template.format(age=age, gender=gender.lower(), gender_cap=gender_cap, personality=personality, accord=chosen_accord, accord_sub=chosen_accord, usage=usage, sillage=sillage_noun, longevity=longevity_noun, price=price_phrase)

        else:  # mixed
            num_accords = random.choices([1,2], weights=[0.8,0.2])[0]
            accords_selected = random.sample(ACCORD_NAMES, k=num_accords)
            notes_pool = []
            for a in accords_selected:
                pool = accord_to_notes.get(a, [])
                if pool:
                    notes_pool.extend(pool)
            if random.random() < 0.2:
                notes_pool.extend(NOTE_NAMES)
            notes_pool = list(dict.fromkeys(notes_pool))
            if not notes_pool:
                notes_pool = NOTE_NAMES
            num_notes = random.choices([1,2,3], weights=[0.6,0.3,0.1])[0]
            notes_selected = random.sample(notes_pool, k=min(num_notes, len(notes_pool)))
            if random.random() < 0.5:
                template = next(mixed_cycle)
                sentence = template.format(age=age, gender=gender.lower(), gender_cap=gender_cap, personality=personality, accords=", ".join(accords_selected), notes=", ".join(notes_selected), usage=usage)
            else:
                # use noun/verb with one accord
                chosen_accord = random.choice(accords_selected)
                if random.random() < 0.5:
                    template = next(template_cycle_noun)
                else:
                    template = next(template_cycle_verb)
                sentence = template.format(age=age, gender=gender.lower(), gender_cap=gender_cap, personality=personality, accord=chosen_accord, accord_sub=chosen_accord, usage=usage, sillage=sillage_noun, longevity=longevity_noun, price=price_phrase)

        # occasionally append sillage/longevity/price for variety
        if random.random() < 0.5:
            sentence = sentence + " " + random.choice([sillage_noun, longevity_noun, price_phrase])

        # Annotate entities
        ents = []
        def add_matches(phrase, label):
            for (s,e) in find_all_occurrences(sentence, phrase):
                ents.append((s,e,label))

        add_matches(str(age), "AGE")
        add_matches(gender, "GENDER")
        add_matches(gender_cap, "GENDER")
        add_matches(personality, "PERSONALITY")

        # annotate accords (category + synonyms)
        for a in accords_selected:
            # match category name
            add_matches(a, "PREFERRED_ACCORD")
            # match synonyms from accord_map
            for syn in accord_map.get(a, []):
                add_matches(syn, "PREFERRED_ACCORD")

        # annotate notes (and map-inferred accords if present in text)
        for n in notes_selected:
            add_matches(n, "NOTE")
            for ia in note_to_accords.get(n, []):
                add_matches(ia, "PREFERRED_ACCORD")

        add_matches(usage, "USAGE_SITUATION")
        add_matches(sillage_noun, "SILLAGE")
        add_matches(sillage_verb, "SILLAGE")
        add_matches(longevity_noun, "LONGEVITY")
        add_matches(longevity_verb, "LONGEVITY")
        add_matches(price_phrase, "PRICE")

        # dedupe
        ents = list(dict.fromkeys(ents))

        if ents:
            TRAIN_DATA.append((sentence, {"entities": ents}))
        else:
            skipped += 1

# summary + save
print(f"Generated {len(TRAIN_DATA)} synthetic NER training samples.")
print(f"Skipped {skipped} samples due to matching error.")

for i, (text, annotation) in enumerate(TRAIN_DATA[:5]):
    print(f"Sample {i+1}:")
    print("Text:", text)
    print("Entities:", annotation["entities"])
    print("-" * 80)

with open("ner_training_data.json", "w", encoding="utf-8") as f:
    json.dump(TRAIN_DATA, f, ensure_ascii=False, indent=2)

print("Saved -> ner_training_data.json")
