import re
import json

with open("backend/retrieval/signal_extractor.py", "r") as f:
    code = f.read()

if "import json" not in code:
    code = code.replace("import re", "import re\nimport json")

# Add split_into_sentences and format_signal
new_funcs = """
def split_into_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n', text) if s.strip()]

def is_low_quality(sentence: str) -> bool:
    if len(sentence.split()) < 5:
        return True
    lower = sentence.lower()
    BAD = ["read more", "press inquiries", "contact", "media@", "learn more", "story"]
    return any(b in lower for b in BAD)

def format_signal(text: str, source_type: str) -> str:
    lower = text.lower()
    conf = 0.50
    if "launches" in lower: conf = 0.95
    elif "released" in lower: conf = 0.90
    elif "introduced" in lower: conf = 0.85
    elif "powers" in lower: conf = 0.75
    elif "helps power" in lower: conf = 0.70
    return json.dumps({
        "text": text,
        "confidence": conf,
        "source_type": source_type
    })

def normalize(signal: str) -> str:
    try:
        obj = json.loads(signal)
        text = obj.get("text", signal)
    except:
        text = signal
    return re.sub(r'\W+', '', text.lower())

"""

if "def split_into_sentences" not in code:
    code = code.replace("# ---------------------------------------------------------------------------", new_funcs + "\n# ---------------------------------------------------------------------------", 1)

patterns = """
SHIPPING_PATTERNS = [
    r"\\b\\d+\\s+launches\\b",
    r"\\bshipped\\b",
    r"\\bshipping\\b",
    r"\\brolling out\\b",
    r"\\breleased\\b",
    r"\\blaunches\\b",
    r"\\bintroduced\\b",
    r"\\bnew products\\b",
    r"\\bnow available\\b",
]

ADOPTION_PATTERNS = [
    r"every company",
    r"customers",
    r"businesses",
    r"expands its use",
    r"millions of users",
    r"adoption",
    r"used by",
    r"growing",
    r"growth",
]
"""
if "SHIPPING_PATTERNS =" not in code:
    code = code.replace("SHIPPING_PATTERNS_DETECT =", patterns + "\nSHIPPING_PATTERNS_DETECT =")

# update deduplicate_signals to use normalize
code = code.replace("normalized = re.sub(r'\W+', '', chunk.lower())", "normalized = normalize(chunk)")

# Replace extract_signals
import ast

old_main = code[code.find("def extract_signals(text: str) -> dict:"):code.find("if __name__ == \"__main__\":")]

new_main = """def extract_signals(text: str) -> dict:
    extracted = defaultdict(list)

    sentences = split_into_sentences(text)
    print(f"[signals] Received {len(sentences)} sentences")

    # Evaluate each sentence independently
    for sentence in sentences:
        if is_low_quality(sentence):
            print(f"[signal rejected] low quality: {sentence[:40]}")
            continue

        # Skip noise
        if is_pricing_or_package_description(sentence) or is_newsletter_description(sentence):
            continue

        sentence_lower = sentence.lower()
        
        # ---- LAUNCH ----
        # Use existing logic for atomic signals (IBM support)
        launch_items = extract_atomic_launch_signals(sentence)
        launch_sentences = extract_sentence_launch_signals(sentence)
        
        for item in launch_items + launch_sentences:
            sig = format_signal(item, "launch")
            extracted["launch_signals"].append(sig)
            print(f"[signal accepted] launch: {item[:80]}")

        # ---- SHIPPING VELOCITY ----
        has_shipping = False
        for pat in SHIPPING_PATTERNS:
            if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                m = re.search(pat, sentence_lower, flags=re.IGNORECASE)
                sig_text = m.group(0)
                sig = format_signal(sig_text, "shipping_velocity")
                extracted["shipping_velocity_signals"].append(sig)
                print(f"[signal accepted] shipping_velocity: {sig_text}")
                has_shipping = True
        
        if not has_shipping:
            # Fallback for IBM
            if any(re.search(pat, sentence_lower, flags=re.IGNORECASE) for pat in SHIPPING_PATTERNS_DETECT):
                items = extract_shipping_velocity(sentence)
                for item in items:
                    sig = format_signal(item, "shipping_velocity")
                    extracted["shipping_velocity_signals"].append(sig)
                    print(f"[signal accepted] shipping_velocity: {item[:60]}")

        # ---- ADOPTION ----
        has_adoption = False
        for pat in ADOPTION_PATTERNS:
            if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                sig = format_signal(sentence, "adoption")
                extracted["adoption_signals"].append(sig)
                print(f"[signal accepted] adoption: {sentence[:60]}")
                has_adoption = True
                break
                
        if not has_adoption:
            for item in extract_adoption_signals(sentence):
                sig = format_signal(item, "adoption")
                extracted["adoption_signals"].append(sig)
                print(f"[signal accepted] adoption: {item[:80]}")

        # ---- PARTNERSHIPS ----
        for item in extract_partnership_signals(sentence):
            sig = format_signal(item, "partnership")
            extracted["partnership_signals"].append(sig)
            print(f"[signal accepted] partnership: {item[:80]}")

        # ---- HIRING ----
        for item in extract_hiring_signals(sentence):
            sig = format_signal(item, "hiring")
            extracted["hiring_signals"].append(sig)
            print(f"[signal accepted] hiring: {item[:80]}")

        # ---- AI INITIATIVES ----
        match_count = sum(sentence_lower.count(kw) for kw in AI_INITIATIVE_KEYWORDS)
        has_action_verb = any(v in sentence_lower for v in AI_ACTION_VERBS)
        if match_count >= 2 and has_action_verb:
            sig = format_signal(sentence, "ai_initiative")
            extracted["ai_initiatives"].append(sig)
            print(f"[signal accepted] ai_initiative: {sentence[:40]}")

        # ---- TECHNICAL ----
        if any(kw in sentence_lower for kw in TECHNICAL_KEYWORDS):
            sig = format_signal(sentence, "technical")
            extracted["technical_signals"].append(sig)

        # ---- ENTERPRISE ----
        if any(kw in sentence_lower for kw in ENTERPRISE_KEYWORDS):
            sig = format_signal(sentence, "enterprise")
            extracted["enterprise_signals"].append(sig)

    if "launch_signals" in extracted:
        extracted["launch_signals"] = _dedup_launch_signals(extracted["launch_signals"])

    deduped = deduplicate_signals(extracted)

    print("\\n" + "=" * 50)
    print("===== SIGNAL AUDIT =====")
    print("=" * 50)
    for cat in ["launch_signals", "shipping_velocity_signals", "adoption_signals",
                "hiring_signals", "partnership_signals"]:
        items = deduped.get(cat, [])
        print(f"{cat}: {len(items)}")
        for ex in items[:5]:
            try:
                obj = json.loads(ex)
                text = obj.get("text", ex)
            except:
                text = ex
            print(f"  - {text[:100]}")
    print("=" * 50)

    return deduped

"""

code = code.replace(old_main, new_main)

# Also update _dedup_launch_signals to parse json
old_dedup = """def _dedup_launch_signals(items: list) -> list:
    # Sort longest-first
    sorted_items = sorted(items, key=len, reverse=True)
    result = []
    for candidate in sorted_items:
        cl = candidate.lower()
        # Skip if this is a substring of something already kept
        if any(cl in kept.lower() for kept in result):
            continue
        result.append(candidate)
    return result"""

new_dedup = """def _dedup_launch_signals(items: list) -> list:
    import json
    def get_text(s):
        try:
            return json.loads(s).get("text", s)
        except:
            return s
            
    sorted_items = sorted(items, key=lambda x: len(get_text(x)), reverse=True)
    result = []
    for candidate in sorted_items:
        cl = get_text(candidate).lower()
        if any(cl in get_text(kept).lower() for kept in result):
            continue
        result.append(candidate)
    return result"""

code = code.replace(old_dedup, new_dedup)

with open("backend/retrieval/signal_extractor.py", "w") as f:
    f.write(code)

print("Patch applied successfully")
