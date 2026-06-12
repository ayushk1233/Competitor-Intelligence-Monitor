import hashlib
import json
import re
from collections import defaultdict


def split_into_sentences(text: str) -> list:
    # Split merged feature lists like "Semantic search Published 2025 Reinforcement learning..."
    text = re.sub(r'(Published 20\d\d)\s+(?=[A-Z])', r'\1. ', text)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n', text) if s.strip()]

def is_low_quality(sentence: str) -> bool:
    lower = sentence.lower()
    if len(sentence.split()) < 5:
        strategic_terms = (
            ENTERPRISE_KEYWORDS
            + TECHNICAL_KEYWORDS
            + HIRING_REQUIRED_TERMS
            + ["partnership", "announced", "launch", "released"]
        )

        if any(term in lower for term in strategic_terms):
            return False

        if re.search(r'Published 20\d\d', sentence, re.IGNORECASE):
            return False

        return True

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


# ---------------------------------------------------------------------------
# PATTERN DEFINITIONS
# ---------------------------------------------------------------------------

ARTIFACT_PATTERNS = [
    r"q=\d+",
    r"w=\d+",
    r"\.jpg",
    r"\.png",
    r"\.webp",
    r"&q=",
    r"&w="
]


# Issue 1: Atomic launch detection — broad, case-insensitive
# Each match yields one atomic event string
LAUNCH_PATTERNS = [
    # Explicit product event phrases
    (r"product\s+announcement[:\s]+(.{5,80})", 1),
    (r"products?\s+announced\s+at\s+(.{5,80})", 1),
    (r"announced\s+at\s+\w+\s*20\d{2}[:\s]+(.{5,80})", 1),
    (r"meet\s+([A-Z][A-Za-z0-9 ®™]{2,50})", 1),      # "Meet IBM Bob"
    (r"introducing\s+([A-Za-z0-9 ®™]{3,60})", 1),     # "Introducing IBM Concert Platform"
    (r"introduces?\s+([A-Za-z0-9 ®™]{3,60})", 1),
    (r"launched?\s+([A-Za-z0-9 ®™]{3,60})", 1),
    (r"released?\s+([A-Za-z0-9 ®™]{3,60})", 1),
    (r"today\s+(?:we\s+)?announced\s+(.{5,80})", 1),
    (r"now\s+available[:\s]+(.{5,80})", 1),
    (r"general\s+availability[:\s]+(.{5,80})", 1),
    (r"public\s+beta[:\s]+(.{5,80})", 1),
    (r"published\s+20\d{2}\s+(.{3,80})", 1),
    (r"ga\s+release[:\s]+(.{5,80})", 1),
    (r"new\s+platform[:\s]+(.{5,80})", 1),
    (r"new\s+product[:\s]+(.{5,80})", 1),
    (r"added\s+support\s+for\s+(.{5,80})", 1),
    (r"([A-Za-z][A-Za-z0-9\- ]{5,40}\s+published\s+20\d\d)", 1),
    (r"(new feature)", 1),
    (r"(feature release)", 1),
    (r"(semantic search)", 1),
    (r"(reinforcement learning)", 1)
]

# Sentence-level launch patterns (Stripe momentum fix)
LAUNCH_SENTENCE_PATTERNS = [
    r"\blaunches\b",
    r"\blaunched\b",
    r"\blaunch\b",
    r"\breleased\b",
    r"\brelease\b",
    r"\brollout\b",
    r"\brolling out\b",
    r"\bnew product\b",
    r"\bnew products\b",
    r"\bintroduced\b",
    r"\bintroducing\b",
    r"\bavailable now\b",
    r"\bnow available\b",
    r"\bships\b",
    r"\bshipping\b",
    r"\bbuilds out\b",
    r"\bpowers\b",
    r"\bhelps power\b"
]

# Issue 5: AI / model launches — STRICT named-product patterns only.
# Do NOT use generic 'multimodal model:' or 'llm:' — these match sentence fragments.
AI_PRODUCT_PATTERNS = [
    (r"(granite(?:\s+vision)?\s+[\d.]+)", 0),        # "Granite Vision 3.0", "Granite 3"
    (r"(granite\s+vision)", 0),                       # "Granite Vision" (no version)
    (r"(watsonx(?:\.[a-z]+)?)", 0),                   # "watsonx", "watsonx.ai"
    (r"new\s+(?:open.source\s+)?(?:ai\s+)?model[:\s]+([A-Z][A-Za-z0-9 ]{2,40})", 1),
    (r"open.source\s+([A-Z][A-Za-z][A-Za-z0-9 ®™]{2,40})", 1),  # "open-source Granite Vision"
]

# Issue 4: Shipping velocity patterns — broad event-level detection

SHIPPING_PATTERNS = [
    r"\b\d+\s+launches\b",
    r"\bshipped\b",
    r"\bshipping\b",
    r"\brolling out\b",
    r"\breleased\b",
    r"\blaunches\b",
    r"\bintroduced\b",
    r"\bnew products\b",
    r"\bnow available\b",
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

INTRODUCING_PATTERNS = [
    r"\bintroducing\b",
    r"\bnew\b",
    r"\bbeta\b",
    r"\bannounced\b",
    r"\bannouncement\b",
    r"\blatest announcements\b",
    r"\bnow available\b",
    r"\bavailable now\b",
    r"\bagent cli\b",
]

HUBSPOT_PRODUCTS = [
    "breeze",
    "agent cli",
    "agentic",
    "copilot",
    "content hub",
    "sales hub",
    "service hub",
    "marketing hub",
    "commerce hub",
    "operations hub",
]

GROWTH_PATTERNS = [
    r"\bover \$\d+ (?:million|billion)\b",
    r"\b\d+k global customers\b",
    r"\brevenue\b",
    r"\bgrowth\b",
]

SHIPPING_PATTERNS_DETECT = [
    r"think\s+20\d{2}",
    r"product\s+announcement",
    r"announced\s+at",
    r"new\s+capability",
    r"new\s+feature",
    r"new\s+platform",
    r"introducing",
    r"meet\s+[A-Z]",
    r"released?",
    r"changelog",
    r"release\s+notes",
]

# Per-line patterns for extracting individual velocity items
SHIPPING_LINE_PATTERNS = [
    (r"introduces?\s+(.+)", 1),
    (r"added\s+support(?:\s+for)?\s+(.+)", 1),
    (r"meet\s+([A-Z][A-Za-z0-9 ®™]{2,50})", 1),
    (r"now\s+available:\s+(.+)", 1),
    (r"product\s+announcement[:\s]+(.{5,80})", 1),
]

# Issue 2: Partnership — broad, sentence-level extraction
PARTNERSHIP_PATTERNS = [
    r"partner(?:ed|ship|ing)?(?:\s+with)?",
    r"collaboration",
    r"joint\s+(?:venture|initiative|effort)",
    r"working\s+with",
    r"alliance",
    r"commit\s+\$",                  # "Commit $5 Billion"
    r"and\s+red\s+hat",
    r"and\s+microsoft",
    r"and\s+aws",
    r"and\s+google",
    r"and\s+openai",
    r"teamed\s+up",
    r"\$\d+\s+billion",              # "$5 Billion" deals
    r"strategic\s+(?:deal|agreement|relationship)",
]

# Issue 3: Adoption — expanded to include market validation
ADOPTION_REGEXES = [
    # Numeric adoption
    r"\d+%\s+of\s+engineers",
    r"\d+%\s+of\s+our\s+(?:org|team|engineers|organization)",
    r"\d+,\d+\s+engineers",
    r"\d+,\d+\s+developers",
    r"over\s+\d+%\s+adoption",
    r"over\s+\d+%\s+of\s+engineers",
    r"growing\s+from\s+\d+\s+to\s+(?:over\s+)?\d+\s+engineers",
    r"adoption\s+(?:went|grew|growing)\s+from\s+\w+\s+to\s+over\s+\d+%",
    r"thousands\s+of\s+users",
    r"millions\s+of\s+users",
    r"used\s+by\s+(?:over\s+)?\d+",
    # Market validation / benchmark performance
    r"(?:ranked|ranking|rank)\s+(?:first|second|third|#1|#2|\d+)\b",
    r"(?:first|second|third)\s+(?:place|in|on)\s+(?:the\s+)?(?:leaderboard|benchmark|ranking)",
    r"leaderboard",
    r"top\s+performer",
    r"top\s+model",
    r"outperforms?",
    r"head.and.shoulders\s+above",
    r"state.of.the.art",
    r"sota",
    r"best.in.class",
    r"industry.leading",
    r"customers?(?:\s+including|\s+such\s+as|\s+like)",
    r"organizations?\s+(?:use|using|rely)",
    r"trusted\s+by",
]

# Issue 4: False positive rejection
FALSE_POSITIVE_PATTERNS = [
    ".py", ".js", ".tsx", ".ts", ".css", ".html",
    "marketing-static", "cdn", "/assets/", "favicon",
    "summary.py", "segmentation.py", "report.py", "test_",
    "http://", "https://", ".com/", ".io/",
]

# Strict hiring — only explicit open-position language
HIRING_REQUIRED_TERMS = [
    "we are hiring",
    "we're hiring",
    "hiring engineers",
    "hiring now",
    "open roles",
    "job openings",
    "recruiting",
    "growing our team",
    "careers page",
    "open positions",
    "apply now",
    "job board",
    "search jobs",
    "job alerts",
]

AI_INITIATIVE_KEYWORDS = [
    "ai agent", "agentic ai", "llm", "foundation model",
    "generative ai", "machine learning", "artificial intelligence",
    "reasoning model"
]

AI_ACTION_VERBS = [
    "announce", "launch", "commit", "release", "introduce",
    "unveil", "expand", "partner", "invest", "acquire",
    "build", "building"
]

TECHNICAL_KEYWORDS = [
    "api", "developer", "platform", "sdk", "infrastructure",
    "framework", "developer tools", "deployment", "observability"
]

ENTERPRISE_KEYWORDS = [
    "enterprise", "security", "compliance", "governance", "scalable",
    "enterprise-grade", "large organizations", "regulated industries"
]

HISTORICAL_TERMS = [
    "years ago", "first released", "founded", "origin story",
    "started the company", "we built", "over the years",
    "for decades", "27 years", "23 years"
]

PRICING_TERMS = [
    "per month", "billed annually", "fixed price",
    "unlimited users", "storage space", "free trial", "payment options"
]

NEWSLETTER_TERMS = [
    "newsletter", "join more than", "stay in touch"
]


# ---------------------------------------------------------------------------
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
    
    import re
    if re.search(r'published 20\d\d', text_val, re.IGNORECASE):
        kw_score += 2.0
    
    if "semantic search" in text_val.lower() or "indexing" in text_val.lower() or "collaboration" in text_val.lower():
        kw_score += 2.0
        
    noise_penalty = 0.5 if len(text_val) > 300 else 0.0
    return length_score + kw_score - noise_penalty

def is_false_positive(text: str) -> bool:
    for pat in FALSE_POSITIVE_PATTERNS:
        if pat in text:
            return True
    return False


def is_pricing_or_package_description(text: str) -> bool:
    lower = text.lower()
    return any(t in lower for t in PRICING_TERMS)


def is_newsletter_description(text: str) -> bool:
    lower = text.lower()
    return any(t in lower for t in NEWSLETTER_TERMS)


def has_historical_context(text: str) -> bool:
    lower = text.lower()
    return any(t in lower for t in HISTORICAL_TERMS)


def has_recent_context(text: str) -> bool:
    lower = text.lower()
    RECENT = ["2024", "2025", "2026", "today", "recently", "announced",
              "launched", "now available", "beta", "general availability"]
    return any(t in lower for t in RECENT)


def clean_capture(text: str) -> str:
    """Strip markdown noise, links, and extra whitespace from a captured group."""
    for pat in ARTIFACT_PATTERNS:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    # Remove markdown link text [...](...) 
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove leftover URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove markdown symbols
    text = re.sub(r'[#\*\[\]]+', '', text)
    text = re.sub(r'^[^a-zA-Z0-9]+', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_atomic_launch_signals(paragraph: str) -> list:
    """
    Issue 1 & 5: Extract individual launch events + AI product launches.
    Each pattern yields one atomic item. Never stores the whole paragraph.
    """
    items = []
    seen = set()

    all_patterns = LAUNCH_PATTERNS + AI_PRODUCT_PATTERNS

    for pattern, group_idx in all_patterns:
        for m in re.finditer(pattern, paragraph, flags=re.IGNORECASE):
            try:
                captured = m.group(group_idx).strip() if m.lastindex and m.lastindex >= group_idx else m.group(0).strip()
            except IndexError:
                captured = m.group(0).strip()
            captured = clean_capture(captured)
            if len(captured) > 3 and not is_false_positive(captured):
                key = captured.lower()[:40]
                if key not in seen:
                    seen.add(key)
                    items.append(captured)

    return items


def extract_sentence_launch_signals(paragraph: str) -> list:
    """
    Sentence-level extraction for launches (fixes Stripe momentum).
    """
    found = []
    sentences = re.split(r'(?<=[.!?])\s+|\n', paragraph)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
            
        lower = sentence.lower()
        for pattern in LAUNCH_SENTENCE_PATTERNS:
            if re.search(pattern, lower, flags=re.IGNORECASE):
                cleaned = clean_capture(sentence)
                if cleaned and not is_false_positive(cleaned):
                    if len(cleaned) >= 20:
                        found.append(cleaned)
                break
    return found


def extract_shipping_velocity(paragraph: str) -> list:
    """
    Issue 4: Extract individual shipping velocity entries.
    Returns one item per feature/announcement line.
    """
    items = []
    seen = set()

    # First try line-level patterns
    for line in paragraph.split('\n'):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        for pattern, group_idx in SHIPPING_LINE_PATTERNS:
            m = re.search(pattern, line, flags=re.IGNORECASE)
            if m:
                try:
                    captured = m.group(group_idx).strip() if m.lastindex and m.lastindex >= group_idx else line
                except IndexError:
                    captured = line
                captured = clean_capture(captured)
                if len(captured) > 5 and not is_false_positive(captured):
                    key = captured.lower()[:40]
                    if key not in seen:
                        seen.add(key)
                        items.append(captured)
                break

    return items


def extract_adoption_signals(paragraph: str) -> list:
    """
    Issue 3: Expanded adoption extraction — numeric evidence + market validation.
    """
    found = []
    seen = set()

    for pattern in ADOPTION_REGEXES:
        for m in re.finditer(pattern, paragraph, flags=re.IGNORECASE):
            # Extract surrounding sentence for context
            start = max(0, m.start() - 60)
            end = min(len(paragraph), m.end() + 60)
            snippet = paragraph[start:end].strip()
            snippet = clean_capture(snippet)
            if snippet and len(snippet) > 5 and not is_false_positive(snippet):
                key = snippet.lower()[:50]
                if key not in seen:
                    seen.add(key)
                    found.append(snippet)

    return found


def extract_partnership_signals(paragraph: str) -> list:
    """
    Issue 2: Sentence-level partnership extraction.
    Returns sentences that contain partnership evidence.
    """
    found = []
    sentences = re.split(r'(?<=[.!?])\s+|\n', paragraph)

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 15:
            continue
        lower = sentence.lower()
        for pattern in PARTNERSHIP_PATTERNS:
            if re.search(pattern, lower, flags=re.IGNORECASE):
                cleaned = clean_capture(sentence)
                if cleaned and len(cleaned) > 10 and not is_false_positive(cleaned):
                    found.append(cleaned)
                break

    return found


def extract_hiring_signals(paragraph: str) -> list:
    """
    Strict hiring — only explicit open-position language.
    Rejects generic 'join our team' / 'careers' without job specifics.
    """
    lower = paragraph.lower()
    for term in HIRING_REQUIRED_TERMS:
        if term in lower:
            return [paragraph.strip()]
    return []


def _dedup_launch_signals(items: list) -> list:
    """
    Remove substrings: if 'Granite' and 'Granite Vision 3' both exist,
    keep only the longest (most specific) form.
    """
    # Sort longest-first
    sorted_items = sorted(items, key=len, reverse=True)
    result = []
    for candidate in sorted_items:
        cl = re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', candidate.lower())).strip()
        # Skip if this is a substring of something already kept
        if any(cl in re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', kept.lower())).strip() for kept in result):
            continue
        result.append(candidate)
    return result


def deduplicate_signals(extracted: dict) -> dict:
    deduped = defaultdict(list)

    for category, chunks in extracted.items():
        seen_hashes = set()

        for chunk in chunks:
            normalized = normalize(chunk)
            chunk_hash = hashlib.md5(
                normalized.encode()
            ).hexdigest()

            if chunk_hash not in seen_hashes:
                seen_hashes.add(chunk_hash)
                deduped[category].append(chunk)

    return dict(deduped)


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def extract_signals(text: str) -> dict:
    extracted = defaultdict(list)

    sentences = split_into_sentences(text)

    # Evaluate each sentence independently
    for sentence in sentences:
        sentence = extract_quote_content(sentence)
        if is_low_quality(sentence):
            continue
        if is_ocr_noise(sentence):
            continue

        # Skip noise
        if is_pricing_or_package_description(sentence) or is_newsletter_description(sentence):
            continue

        # Skip historical references
        if has_historical_context(sentence) and not has_recent_context(sentence):
            continue

        sentence_lower = sentence.lower()
        
        # ---- PRIORITY LAUNCH (HubSpot) ----
        has_priority_launch = False
        
        for pat in INTRODUCING_PATTERNS:
            if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                sig = format_signal(sentence, "launch")
                extracted["launch_signals"].insert(0, sig)
                has_priority_launch = True
                break
                
        if not has_priority_launch:
            for prod in HUBSPOT_PRODUCTS:
                if prod in sentence_lower:
                    sig = format_signal(sentence + " [announced]", "launch")
                    extracted["launch_signals"].append(sig)
                    has_priority_launch = True
                    break
        
        # ---- PRIORITY GROWTH (HubSpot) ----
        has_priority_growth = False
        for pat in GROWTH_PATTERNS:
            if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                sig = format_signal(sentence, "adoption")
                extracted["adoption_signals"].insert(0, sig)
                has_priority_growth = True
                break
                
        if has_priority_launch or has_priority_growth:
            continue
        
        # ---- LAUNCH ----
        launch_items = extract_atomic_launch_signals(sentence)
        launch_sentences = extract_sentence_launch_signals(sentence)
        
        for item in launch_items + launch_sentences:
            sig = format_signal(item, "launch")
            extracted["launch_signals"].append(sig)

        # ---- SHIPPING VELOCITY ----
        has_shipping = False
        for pat in SHIPPING_PATTERNS:
            if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                m = re.search(pat, sentence_lower, flags=re.IGNORECASE)
                sig_text = m.group(0)
                sig = format_signal(sig_text, "shipping_velocity")
                extracted["shipping_velocity_signals"].append(sig)
                has_shipping = True
        
        if not has_shipping:
            if any(re.search(pat, sentence_lower, flags=re.IGNORECASE) for pat in SHIPPING_PATTERNS_DETECT):
                items = extract_shipping_velocity(sentence)
                for item in items:
                    sig = format_signal(item, "shipping_velocity")
                    extracted["shipping_velocity_signals"].append(sig)

        # ---- ADOPTION ----
        has_adoption = False
        for pat in ADOPTION_PATTERNS:
            if re.search(pat, sentence_lower, flags=re.IGNORECASE):
                sig = format_signal(sentence, "adoption")
                extracted["adoption_signals"].append(sig)
                has_adoption = True
                break
                
        if not has_adoption:
            for item in extract_adoption_signals(sentence):
                sig = format_signal(item, "adoption")
                extracted["adoption_signals"].append(sig)

        # ---- PARTNERSHIPS ----
        for item in extract_partnership_signals(sentence):
            sig = format_signal(item, "partnership")
            extracted["partnership_signals"].append(sig)

        # ---- HIRING ----
        for item in extract_hiring_signals(sentence):
            sig = format_signal(item, "hiring")
            extracted["hiring_signals"].append(sig)

        # ---- AI INITIATIVES ----
        has_action_verb = any(
            v in sentence_lower
            for v in AI_ACTION_VERBS
        )

        has_ai_keyword = any(
            kw in sentence_lower
            for kw in AI_INITIATIVE_KEYWORDS
        )

        if has_ai_keyword and has_action_verb:
            sig = format_signal(sentence, "ai_initiative")
            extracted["ai_initiatives"].append(sig)

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

    print(f"  [signals] extracted: {sum(len(v) for v in deduped.values())} signals across {len(deduped)} categories")

    # Apply ranking
    for cat in ["launch_signals", "adoption_signals", "partnership_signals"]:
        if cat in deduped:
            deduped[cat] = sorted(deduped[cat], key=calculate_quality_score, reverse=True)[:10]

    # Revert signal objects back into plain strings to fix Pydantic validation
    final_signals = defaultdict(list)
    for cat, items in deduped.items():
        for ex in items:
            try:
                obj = json.loads(ex)
                text = obj.get("text", ex)
            except:
                text = ex
            # Neutralize double quotes to prevent downstream LLM JSON errors
            text = text.replace('"', "'")
            print(f"[debug] {cat} signal type: {type(text)}")
            final_signals[cat].append(text)

    return dict(final_signals)

if __name__ == "__main__":

    sample = """
    Products announced at Think 2026 — Meet IBM Bob, your SDLC partner.
    Introducing IBM Concert Platform: Closing the gap between insight and action.

    IBM and Red Hat Commit $5 Billion to Redefine the Future of Open Source in the AI Era.

    Granite Vision 3 achieved second place on OCRBench leaderboard,
    head-and-shoulders above any other small model.

    adoption growing from 150 to over 500 engineers (~60% of our org!)

    We are hiring engineers. Search Jobs. Open roles in ML and infrastructure.
    """

    signals = extract_signals(sample)
    from pprint import pprint
    pprint(signals)