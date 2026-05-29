import re


HIGH_SIGNAL_KEYWORDS = {

    # AI / innovation
    "ai": 3,
    "llm": 3,
    "agent": 3,
    "automation": 2,
    "copilot": 3,
    "agentic": 3,
    "assistant": 2,
    "workflow automation": 3,
    "reasoning model": 4,
    "foundation model": 4,
    "ai platform": 4,
    "ai infrastructure": 4,
    "genai": 3,
    "generative ai": 3,
    "machine learning": 2,

    # launches
    "launch": 3,
    "release": 2,
    "introducing": 2,
    "announcement": 2,
    "new feature": 3,
    "rollout": 3,
    "preview": 3,
    "beta": 3,
    "general availability": 4,
    "ga": 3,
    "new capability": 3,
    "new product": 4,
    "debut": 3,
    "unveiled": 3,
    "introduced": 2,
    "announced": 2,

    # hiring / growth
    "hiring": 3,
    "careers": 2,
    "join us": 2,
    "jobs": 2,
    "expanding": 2,
    "expanding team": 3,
    "open roles": 2,
    "recruiting": 3,
    "growing engineering": 3,
    "hiring globally": 3,
    "career opportunities": 2,

    # product / infra
    "api": 2,
    "developer": 2,
    "platform": 2,
    "infrastructure": 2,
    "sdk": 3,
    "framework": 2,
    "developer tools": 3,
    "deployment": 2,
    "observability": 2,

    # enterprise / market
    "enterprise": 1,
    "security": 1,
    "compliance": 1,
    "governance": 2,
    "scalable": 1,
    "enterprise-grade": 3,
    "large organizations": 2,
    "regulated industries": 2,

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