def classify_page_type(
    url: str
):

    lower = url.lower()

    if "careers" in lower or "jobs" in lower:
        return "careers"

    if "pricing" in lower:
        return "pricing"

    if "docs" in lower or "developers" in lower:
        return "docs"

    # Issue 3: Granular news/press/blog classification.
    # Priority order matters — newsroom before generic news.
    if "newsroom" in lower:
        return "news"

    if "press" in lower:
        return "press"

    if "blog" in lower:
        return "blog"

    if "news" in lower:
        return "news"

    if "announcement" in lower or "launches" in lower:
        return "launches"

    if "research" in lower:
        return "research"

    if "changelog" in lower:
        return "changelog"

    return "homepage"


if __name__ == "__main__":

    urls = [
        "https://example.com/",
        "https://example.com/careers",
        "https://example.com/pricing",
        "https://example.com/docs/api",
        "https://example.com/blog/new-feature",
        "https://example.com/jobs/engineer",
        "https://example.com/developers",
    ]

    for url in urls:

        page_type = classify_page_type(url)

        print(f"{url} → {page_type}")
