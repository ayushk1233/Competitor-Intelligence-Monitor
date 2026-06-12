import re

MAX_SIGNALS_PER_TYPE = 3

# Marketing noise patterns — generic claims that are not real signals
MARKETING_NOISE_PATTERNS = [
    r"capture\s+new\s+leads?",
    r"close\s+more\s+deals?",
    r"drive\s+(more\s+)?revenue",
    r"increase\s+(sales|revenue|productivity)",
    r"grow\s+(your\s+)?business",
    r"accelerate\s+(your\s+)?growth",
    r"unlock\s+(your\s+)?potential",
    r"transform\s+(your\s+)?business",
    r"next.generation\s+(platform|solution|ai)",
    r"industry.leading",
    r"best.in.class",
    r"cutting.edge",
    r"game.changing",
    r"revolutionary",
    r"breakthrough",
    r"all.in.one\s+(platform|solution)",
    r"end.to.end\s+(platform|solution)",
    r"enterprise.grade\s+(platform|solution)",
    r"world.class",
    r"market.leading",
    r"trusted\s+by\s+(thousands|millions|leading)",
    r"streamline\s+(your\s+)?(workflow|process|operations)",
    r"optimize\s+(your\s+)?(workflow|process|operations)",
    r"supercharge\s+(your\s+)?(team|workflow|productivity)",
    r"empower\s+(your\s+)?(team|organization|business)",
    r"future.of\s+(work|ai|software)",
    r"platform\s+for\s+(modern|today.s)\s+(teams?|enterprise|business)",
    r"built\s+for\s+(modern|today.s)\s+(teams?|enterprise|business)",
    r"designed\s+for\s+(modern|today.s)\s+(teams?|enterprise|business)",
    r"the\s+(best|leading|ultimate)\s+(way|platform|solution)\s+to",
]

ALLOWED_SIGNAL_TYPES = [
    "launch_signals",
    "shipping_velocity_signals",
    "adoption_signals",
    "hiring_signals",
    "partnership_signals",
    "ai_initiatives",
]


def is_marketing_noise(text: str) -> bool:
    """Check if a signal text is generic marketing copy rather than a real signal."""
    lower = text.lower()
    for pattern in MARKETING_NOISE_PATTERNS:
        if re.search(pattern, lower):
            return True
    return False


def is_real_signal(text: str) -> bool:
    """A real signal must reference a specific event, feature, launch, or data point."""
    SIGNAL_TERMS = [
        "launch", "launched", "launches", "released", "release",
        "announced", "announcement", "introducing", "introduced",
        "published", "changelog", "update", "new feature",
        "added support", "now available", "beta", "general availability",
        "partnership", "partnered", "partnering",
        "acquisition", "acquired", "acquiring",
        "funding", "raised", "series", "investment",
        "hiring", "open roles", "job openings", "careers",
        "pricing", "price", "per seat", "per month", "billed annually",
        "% of", "engineers", "adoption", "users",
        "expansion", "expanding", "new market",
        "research", "paper", "benchmark",
        "granite", "watsonx", "breeze", "agent cli",
        "think 20", "commit $", "billion",
    ]
    lower = text.lower()
    return any(t in lower for t in SIGNAL_TERMS)


def validate_signals(
    signals: dict
) -> dict:
    """
    Validate signals: remove marketing noise, only keep real signals.
    """
    validated = {}
    for signal_type, evidence_list in signals.items():
        clean = []
        for evidence in evidence_list:
            if is_marketing_noise(evidence) and not is_real_signal(evidence):
                continue
            clean.append(evidence)
        if clean:
            validated[signal_type] = clean
    return validated


def compress_signals(
    signals: dict
):
    # First: validate — remove marketing noise
    signals = validate_signals(signals)

    compressed = {}

    for (
        signal_type,
        evidence_list
    ) in signals.items():

        unique = []

        seen = set()

        for evidence in evidence_list:

            normalized = (
                evidence.lower().strip()
            )

            if normalized in seen:
                continue

            seen.add(normalized)

            unique.append(evidence)

        compressed[signal_type] = (
            unique[
                :MAX_SIGNALS_PER_TYPE
            ]
        )

    return compressed

if __name__ == "__main__":

    sample = {

        "launch_signals": [
            "Introducing our AI platform.",
            "Introducing our AI platform.",
            "Capture new leads and close more deals",
            "New AI agent release.",
            "Industry-leading next-generation platform",
        ]
    }

    compressed = compress_signals(
        sample
    )

    print(compressed)
