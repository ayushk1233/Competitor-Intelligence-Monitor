import re

with open('backend/retrieval/signal_extractor.py', 'r') as f:
    content = f.read()

# PROBLEM 1: ARTIFACT_PATTERNS
artifact_str = """# ---------------------------------------------------------------------------
# PATTERN DEFINITIONS
# ---------------------------------------------------------------------------

ARTIFACT_PATTERNS = [
    r"q=\d+",
    r"w=\d+",
    r"\\.jpg",
    r"\\.png",
    r"\\.webp",
    r"&q=",
    r"&w="
]
"""
content = content.replace("""# ---------------------------------------------------------------------------
# PATTERN DEFINITIONS
# ---------------------------------------------------------------------------""", artifact_str)

# Update clean_capture
clean_cap_old = """def clean_capture(text: str) -> str:
    \"\"\"Strip markdown noise, links, and extra whitespace from a captured group.\"\"\"
    # Remove markdown link text [...](...) """
clean_cap_new = """def clean_capture(text: str) -> str:
    \"\"\"Strip markdown noise, links, and extra whitespace from a captured group.\"\"\"
    for pat in ARTIFACT_PATTERNS:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    # Remove markdown link text [...](...) """
content = content.replace(clean_cap_old, clean_cap_new)

clean_cap_end_old = """    # Remove markdown symbols
    text = re.sub(r'[#\*\[\]]+', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text"""
clean_cap_end_new = """    # Remove markdown symbols
    text = re.sub(r'[#\*\[\]]+', '', text)
    text = re.sub(r'^[^a-zA-Z0-9]+', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text"""
content = content.replace(clean_cap_end_old, clean_cap_end_new)


# PROBLEM 2 & 3: OCR Noise and Quote Normalization
helpers_old = """# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def is_false_positive(text: str) -> bool:"""
helpers_new = """# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def is_ocr_noise(text: str) -> bool:
    words = text.split()
    if not words:
        return False
    avg_len = sum(len(w) for w in words) / len(words)
    single_char_count = sum(1 for w in words if len(w) == 1)
    single_char_ratio = single_char_count / len(words)
    return avg_len < 2.2 or single_char_ratio > 0.4

def extract_quote_content(text: str) -> str:
    if ">" in text:
        return text.split(">", 1)[1].strip()
    return text

def calculate_quality_score(text: str) -> float:
    try:
        import json
        obj = json.loads(text)
        text_val = obj.get("text", text)
    except:
        text_val = text
        
    length_score = min(len(text_val) / 100.0, 1.0)
    keywords = ["launch", "release", "new", "percent", "%", "million", "billion", "growth", "engineers", "developers", "adoption", "published", "feature"]
    kw_score = sum(0.5 for kw in keywords if kw in text_val.lower())
    noise_penalty = 0.5 if len(text_val) > 300 else 0.0
    return length_score + kw_score - noise_penalty

def is_false_positive(text: str) -> bool:"""
content = content.replace(helpers_old, helpers_new)

# PROBLEM 4: SIGNAL RE-CATEGORIZATION
launch_patterns_old = """    r"\\bhelps power\\b"
]"""
launch_patterns_new = """    r"\\bhelps power\\b",
    r"published\\s+20\\d\\d",
    r"new feature",
    r"feature release",
    r"agent",
    r"indexing",
    r"semantic search",
    r"reinforcement learning"
]"""
content = content.replace(launch_patterns_old, launch_patterns_new)

shipping_detect_old = """    r"introducing",
    r"meet\\s+[A-Z]",
    r"released?",
    r"published\\s+20\\d{2}",
    r"changelog",
    r"release\\s+notes",
]"""
shipping_detect_new = """    r"introducing",
    r"meet\\s+[A-Z]",
    r"released?",
    r"changelog",
    r"release\\s+notes",
]"""
content = content.replace(shipping_detect_old, shipping_detect_new)

# Also remove from SHIPPING_LINE_PATTERNS
shipping_line_old = """# Per-line patterns for extracting individual velocity items
SHIPPING_LINE_PATTERNS = [
    (r"published\\s+20\\d{2}\\s+(.+)", 1),
    (r"introduces?\\s+(.+)", 1),"""
shipping_line_new = """# Per-line patterns for extracting individual velocity items
SHIPPING_LINE_PATTERNS = [
    (r"introduces?\\s+(.+)", 1),"""
content = content.replace(shipping_line_old, shipping_line_new)

# PROBLEM 5: DUPLICATE SIGNALS
dedup_old = """        cl = candidate.lower()
        # Skip if this is a substring of something already kept
        if any(cl in kept.lower() for kept in result):
            continue"""
dedup_new = """        cl = re.sub(r'\\s+', ' ', re.sub(r'[^\\w\\s]', '', candidate.lower())).strip()
        # Skip if this is a substring of something already kept
        if any(cl in re.sub(r'\\s+', ' ', re.sub(r'[^\\w\\s]', '', kept.lower())).strip() for kept in result):
            continue"""
content = content.replace(dedup_old, dedup_new)


# Apply quote extraction and OCR filtering at loop start
loop_start_old = """    # Evaluate each sentence independently
    for sentence in sentences:
        if is_low_quality(sentence):
            print(f"[signal rejected] low quality: {sentence[:40]}")
            continue"""
loop_start_new = """    # Evaluate each sentence independently
    for sentence in sentences:
        sentence = extract_quote_content(sentence)
        if is_low_quality(sentence):
            print(f"[signal rejected]\\n[low quality]\\n[{sentence[:40]}]\\n")
            continue
        if is_ocr_noise(sentence):
            print(f"[signal rejected]\\n[ocr noise]\\n[{sentence[:40]}]\\n")
            continue"""
content = content.replace(loop_start_old, loop_start_new)


# PROBLEM 7: Replace all [signal accepted] prints
content = re.sub(r'print\(f"\[signal accepted\] (.*?): \{(.*?)\}"\)', r'print(f"[signal accepted]\\n[\1]\\n[{\2}]\\n")', content)
content = re.sub(r'print\(f"\[launch accepted\] \{(.*?)\}"\)', r'print(f"[signal accepted]\\n[launch]\\n[{\1}]\\n")', content)
content = re.sub(r'print\(f"\[growth accepted\] \{(.*?)\}"\)', r'print(f"[signal accepted]\\n[adoption]\\n[{\1}]\\n")', content)

# PROBLEM 6: SIGNAL RANKING
ranking_old = """    # Revert signal objects back into plain strings to fix Pydantic validation
    final_signals = defaultdict(list)
    for cat, items in deduped.items():
        for ex in items:"""
ranking_new = """    # Apply ranking
    for cat in ["launch_signals", "adoption_signals", "partnership_signals"]:
        if cat in deduped:
            deduped[cat] = sorted(deduped[cat], key=calculate_quality_score, reverse=True)[:10]

    # Revert signal objects back into plain strings to fix Pydantic validation
    final_signals = defaultdict(list)
    for cat, items in deduped.items():
        for ex in items:"""
content = content.replace(ranking_old, ranking_new)


with open('backend/retrieval/signal_extractor.py', 'w') as f:
    f.write(content)

