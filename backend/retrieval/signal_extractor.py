SIGNAL_PATTERNS = {

    "ai_initiatives": [

        "ai",
        "llm",
        "agent",
        "copilot",
        "automation"
    ],

    "launch_signals": [

        "launch",
        "release",
        "introducing",
        "announcement",
        "new feature"
    ],

    "hiring_signals": [

        "hiring",
        "careers",
        "join us",
        "jobs",
        "expanding team"
    ],

    "technical_signals": [

        "api",
        "developer",
        "platform",
        "sdk",
        "infrastructure"
    ],

    "enterprise_signals": [

        "enterprise",
        "security",
        "compliance",
        "governance",
        "scalable"
    ]
}


import re
from collections import defaultdict


def extract_signals(
    text: str
):

    extracted = defaultdict(list)

    # -----------------------------
    # Split into sentences
    # -----------------------------

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    # -----------------------------
    # Match signals
    # -----------------------------

    for sentence in sentences:

        sentence_lower = (
            sentence.lower()
        )

        for (
            signal_type,
            keywords
        ) in SIGNAL_PATTERNS.items():

            for keyword in keywords:

                if keyword in sentence_lower:

                    extracted[
                        signal_type
                    ].append(
                        sentence.strip()
                    )

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