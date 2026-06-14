import json
import re
import json_repair

def extract_json_block(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```", "", text, flags=re.MULTILINE)
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return text
    return text[start:end + 1]

def safe_json_loads(text: str):
    cleaned = extract_json_block(text)
    try:
        return json_repair.loads(cleaned)
    except Exception as e:
        raise ValueError(f"Malformed JSON: {e}")