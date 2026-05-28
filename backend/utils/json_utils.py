import json
import re


def extract_json_block(text: str) -> str:

    text = text.strip()

    # Remove markdown fences
    text = re.sub(
        r"^```json",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"^```",
        "",
        text,
        flags=re.MULTILINE
    )

    text = text.strip()

    # Find first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON object found"
        )

    return text[start:end + 1]

def safe_json_loads(text: str):

    cleaned = extract_json_block(text)

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Malformed JSON: {e}"
        )