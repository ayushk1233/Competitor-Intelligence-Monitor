from urllib.parse import urlparse


PAGE_TYPE_WEIGHTS = {

    # high strategic value
    "careers": 3,
    "jobs": 3,
    "hiring": 3,

    "blog": 2,
    "news": 2,
    "announcement": 3,
    "launch": 3,

    "docs": 2,
    "developers": 2,
    "api": 2,

    "pricing": 2,
    "enterprise": 2,

    # default
    "homepage": 1
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