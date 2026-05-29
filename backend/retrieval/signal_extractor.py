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
    ]
}


import re
from collections import defaultdict


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

        for (
            signal_type,
            keywords
        ) in SIGNAL_PATTERNS.items():

            if signal_type == "ai_initiatives":
                match_count = sum(paragraph_lower.count(kw) for kw in keywords)
                if match_count >= 2:
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
            else:
                for keyword in keywords:
                    if keyword in paragraph_lower:
                        extracted[signal_type].append(paragraph.strip())
                        print(f"[signals] Matched {signal_type}")
                        break

    return dict(extracted)

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