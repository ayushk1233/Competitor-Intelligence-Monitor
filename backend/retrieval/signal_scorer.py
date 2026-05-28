import re


HIGH_SIGNAL_KEYWORDS = {

    # AI / innovation
    "ai": 3,
    "llm": 3,
    "agent": 3,
    "automation": 2,
    "copilot": 3,

    # launches
    "launch": 3,
    "release": 2,
    "new": 1,
    "introducing": 2,
    "announcement": 2,

    # hiring / growth
    "hiring": 3,
    "careers": 2,
    "join us": 2,
    "jobs": 2,
    "expanding": 2,

    # product / infra
    "api": 2,
    "developer": 2,
    "platform": 2,
    "infrastructure": 2,

    # enterprise / market
    "enterprise": 1,
    "security": 1,
    "compliance": 1,

    # startup velocity
    "fast": 1,
    "rapid": 2,
    "scale": 2,
    "growth": 2
}


def score_text_signal(text: str) -> int:

    text = text.lower()

    score = 0

    for keyword, weight in (
        HIGH_SIGNAL_KEYWORDS.items()
    ):

        matches = len(
            re.findall(
                rf"\b{re.escape(keyword)}\b",
                text
            )
        )

        score += matches * weight

    return score

if __name__ == "__main__":

    sample = """
    Introducing our new AI platform.
    We are rapidly hiring engineers
    to expand our developer API.
    """

    print(
        score_text_signal(sample)
    )