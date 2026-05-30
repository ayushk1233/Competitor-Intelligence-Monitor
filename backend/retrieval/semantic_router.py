from urllib.parse import urlparse


PAGE_TYPE_WEIGHTS = {

    # high strategic value (Boost pages)
    "news": 5,
    "blog": 5,
    "press": 5,
    "releases": 5,
    "changelog": 5,
    "announcement": 5,
    "launch": 5,

    "careers": 3,
    "jobs": 3,
    "hiring": 3,

    "docs": 2,
    "developers": 2,
    "api": 2,
    "pricing": 2,
    "enterprise": 2,

    # Lower priority
    "product": 0,
    "features": 0,
    "marketing": 0,
    "homepage": 0
}


BAD_URL_PATTERNS = [
    "linkedin",
    "/contact",
    "/support",
    "/help",
    "/privacy",
    "/terms",
    "/legal",
    "/cookie",
]


def detect_page_weight(
    url: str
) -> int:

    url_lower = url.lower()

    # Penalize useless pages heavily
    for bad in BAD_URL_PATTERNS:
        if bad in url_lower:
            return -100

    for keyword, weight in (
        PAGE_TYPE_WEIGHTS.items()
    ):

        if keyword in url_lower:
            return weight

    return PAGE_TYPE_WEIGHTS[
        "homepage"
    ]

if __name__ == "__main__":

    urls = [

        "https://cursor.com/careers",

        "https://stripe.com/docs",

        "https://ibm.com",

        "https://hubspot.com/pricing"
    ]

    for url in urls:

        print(
            url,
            "->",
            detect_page_weight(url)
        )