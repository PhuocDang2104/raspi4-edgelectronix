import spacy
from ner_normalize import normalize_entity

def build_request_json(doc):
    """Convert NER doc → JSON request cho UART."""
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

        # GOM THEO LABEL
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
            # Tạm bỏ qua, hoặc bạn muốn thêm field age thì thêm
            pass

    # Loại bỏ trùng lặp trong list
    request["notes"] = list(set(request["notes"]))
    request["preferred_accord"] = list(set(request["preferred_accord"]))

    return request


# ================== DEMO ==================
if __name__ == "__main__":
    nlp_ner = spacy.load("./output/model-last")
    test_text = "I'm 20 years old male I want ambroxan and amber, ocean and tobacco, i want something that lasts long and has light sillage, something that is cheap also"
    doc = nlp_ner(test_text)

    result = build_request_json(doc)

    import json
    print(json.dumps(result, indent=2))