SIGNAL_PATTERNS = {

    "ai_initiatives": [
        "ai agent", "agentic ai", "llm", "foundation model", 
        "generative ai", "machine learning", "artificial intelligence", 
        "reasoning model"
    ],

    "launch_signals": [
        "today announced",
        "today we announced",
        "launched",
        "new product",
        "general availability",
        "ga",
        "public beta",
        "now available",
        "introduced a new",
    ],

    "hiring_signals": [
        "hiring", "careers", "join us", "jobs", "expanding team",
        "open roles", "recruiting", "growing engineering", "hiring globally",
        "career opportunities"
    ],

    "technical_signals": [
        "api", "developer", "platform", "sdk", "infrastructure",
        "framework", "developer tools", "deployment", "observability"
    ],

    "enterprise_signals": [
        "enterprise", "security", "compliance", "governance", "scalable",
        "enterprise-grade", "large organizations", "regulated industries"
    ],

    "partnership_signals": [
        "partnership", "partnered", "teamed up", "alliance", 
        "joint venture", "collaboration with"
    ],
}

# Regex patterns to extract individual shipping velocity items from changelog-style content
SHIPPING_VELOCITY_LINE_PATTERNS = [
    r"published\s+20\d\d\s+(.+)",
    r"released?\s+(.+)",
    r"introduces?\s+(.+)",
    r"added support\s+(?:for\s+)?(.+)",
    r"(?:^|\n)(?:new|update)[:\s]+(.+)",
    r"(?:^|\n)-\s+(.+)",
]

# Regex patterns to detect adoption metrics
ADOPTION_REGEXES = [
    r"\d+%\s+of\s+engineers",
    r"\d+,\d+\s+engineers",
    r"over\s+\d+%\s+adoption",
    r"adoption.*?\d+.*?\d+",
    r"growing\s+from\s+.+?to\s+.+?engineers",
    r"thousands\s+of\s+users",
    r"millions\s+of\s+users",
    r"used\s+by\s+.+?engineers",
    r"\d+,\d+\s+developers",
    r"\d+%\s+of\s+our\s+(?:org|team|engineers)",
]


import re
from collections import defaultdict
import hashlib

def deduplicate_signals(extracted: dict) -> dict:
    seen_hashes = set()
    deduped = defaultdict(list)
    
    # Priority order for deduplication
    priority = [
        "launch_signals",
        "adoption_signals",
        "partnership_signals",
        "shipping_velocity_signals",
        "hiring_signals",
        "technical_signals",
        "enterprise_signals",
        "ai_initiatives"
    ]
    
    for category in priority:
        if category in extracted:
            for chunk in extracted[category]:
                # Normalize chunk text
                normalized = re.sub(r'\W+', '', chunk.lower())
                chunk_hash = hashlib.md5(normalized.encode()).hexdigest()
                
                if chunk_hash not in seen_hashes:
                    seen_hashes.add(chunk_hash)
                    deduped[category].append(chunk)
                    
    # Handle any remaining categories not in priority list
    for category, chunks in extracted.items():
        if category not in priority:
            for chunk in chunks:
                normalized = re.sub(r'\W+', '', chunk.lower())
                chunk_hash = hashlib.md5(normalized.encode()).hexdigest()
                if chunk_hash not in seen_hashes:
                    seen_hashes.add(chunk_hash)
                    deduped[category].append(chunk)
                    
    return dict(deduped)


def is_pricing_or_package_description(text: str) -> bool:
    lower_text = text.lower()
    PRICING_TERMS = [
        "per month", "$299", "billed annually", "fixed price",
        "unlimited users", "storage space", "free trial", "payment options"
    ]
    return any(term in lower_text for term in PRICING_TERMS)

def is_newsletter_description(text: str) -> bool:
    lower_text = text.lower()
    NEWSLETTER_TERMS = [
        "newsletter", "join more than", "product updates", "stay in touch"
    ]
    return any(term in lower_text for term in NEWSLETTER_TERMS)

def has_recent_launch_context(text: str) -> bool:
    lower_text = text.lower()
    
    HISTORICAL_TERMS = [
        "years ago",
        "first released",
        "founded",
        "origin story",
        "started the company",
        "we built",
        "over the years",
        "for decades",
        "27 years",
        "23 years"
    ]
    if any(term in lower_text for term in HISTORICAL_TERMS):
        return False
        
    RECENT_TERMS = [
        "2025",
        "2026",
        "today",
        "recently",
        "new",
        "launching",
        "announced",
        "now available",
        "beta",
        "general availability",
        "ga"
    ]
    if not any(term in lower_text for term in RECENT_TERMS):
        return False
        
    return True


def extract_granular_signals(paragraph: str) -> list[str]:
    """
    For changelog-style paragraphs, extract each individual release/feature
    as a separate signal rather than storing the whole block.
    """
    items = []
    lines = paragraph.split('\n')
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
            continue
        line_lower = line.lower()
        for pattern in SHIPPING_VELOCITY_LINE_PATTERNS:
            m = re.search(pattern, line_lower)
            if m:
                # extract the captured group if present, else use the line
                captured = m.group(1).strip() if m.lastindex else line
                if len(captured) > 5:
                    items.append(captured)
                break
    # If no line-level extraction worked, fall back to the whole paragraph
    if not items:
        items.append(paragraph.strip())
    return items


def extract_adoption_signals(paragraph: str) -> list[str]:
    """
    Use regex to extract individual adoption metrics from a paragraph.
    """
    found = []
    for pattern in ADOPTION_REGEXES:
        for m in re.finditer(pattern, paragraph, flags=re.IGNORECASE):
            match_text = m.group(0).strip()
            if match_text and len(match_text) > 5:
                found.append(match_text)
    return found


def extract_signals(
    text: str
):

    extracted = defaultdict(list)

    # ---------------------------------------------------
    # Split on paragraph boundaries, NOT sentence endings.
    # Sentence splitting (r'(?<=[.!?])\s+') destroys
    # semantic coherence and creates 100+ micro-fragments.
    # Paragraph-level splitting yields 5-15 meaningful
    # evidence units per company.
    # ---------------------------------------------------

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip() and len(p.strip()) > 30
    ]

    print(
        f"[signals] Received {len(paragraphs)} chunks"
    )

    for i, chunk in enumerate(paragraphs[:3]):

        print(f"\n[signals] Sample Chunk {i+1}")

        print(chunk[:400])

        print("-" * 40)

    # ---------------------------------------------------
    # Match signals against each paragraph
    # ---------------------------------------------------

    for paragraph in paragraphs:

        paragraph_lower = paragraph.lower()

        # ---- Adoption: regex-based extraction (runs for every paragraph) ----
        adoption_items = extract_adoption_signals(paragraph)
        for item in adoption_items:
            extracted["adoption_signals"].append(item)
            print(f"[signals] Matched adoption_signals: {item[:80]}")

        for (
            signal_type,
            keywords
        ) in SIGNAL_PATTERNS.items():

            # Skip adoption here; handled above
            if signal_type == "adoption_signals":
                continue

            if signal_type == "ai_initiatives":
                match_count = sum(paragraph_lower.count(kw) for kw in keywords)
                action_verbs = ["announce", "launch", "commit", "release", "introduce", "unveil", "expand", "partner", "invest", "acquire"]
                has_action_verb = any(v in paragraph_lower for v in action_verbs)
                if match_count >= 2 and has_action_verb:
                    extracted[signal_type].append(paragraph.strip())
                    print(f"[signals] Matched {signal_type} (score: {match_count})")

            elif signal_type == "launch_signals":
                if is_pricing_or_package_description(paragraph):
                    continue
                if is_newsletter_description(paragraph):
                    continue
                if has_recent_launch_context(paragraph):
                    for keyword in keywords:
                        if keyword in paragraph_lower:
                            extracted[signal_type].append(paragraph.strip())
                            print(f"[signals] Matched {signal_type}")
                            break

            elif signal_type == "shipping_velocity_signals":
                # Check if this is a changelog-style paragraph
                is_changelog = any(k in paragraph_lower for k in [
                    "published 2024", "published 2025", "published 2026",
                    "changelog", "release notes"
                ])
                for keyword in keywords:
                    if keyword in paragraph_lower:
                        if is_changelog:
                            # Extract granularly
                            items = extract_granular_signals(paragraph)
                            for item in items:
                                extracted[signal_type].append(item)
                                print(f"[signals] Matched shipping_velocity_signals (granular): {item[:60]}")
                        else:
                            extracted[signal_type].append(paragraph.strip())
                            print(f"[signals] Matched {signal_type}")
                        break

            else:
                for keyword in keywords:
                    if keyword in paragraph_lower:
                        extracted[signal_type].append(paragraph.strip())
                        print(f"[signals] Matched {signal_type}")
                        break

    deduped_signals = deduplicate_signals(extracted)
    
    print("\n" + "="*50)
    print("SIGNAL AUDIT")
    print("="*50)
    for cat in ["launch_signals", "shipping_velocity_signals", "adoption_signals", "hiring_signals", "partnership_signals"]:
        items = deduped_signals.get(cat, [])
        print(f"{cat}: {len(items)}")
        for ex in items[:3]:
            print(f"  - {ex[:100]}")
    print("="*50)
        
    return deduped_signals

if __name__ == "__main__":

    sample = """
    Introducing our new AI agent platform.

    We are hiring engineers
    to expand our developer API.

    Enterprise customers can
    now use advanced security
    controls.
    """

    signals = extract_signals(
        sample
    )

    print(signals)