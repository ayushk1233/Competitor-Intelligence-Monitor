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

    if "blog" in lower or "news" in lower:
        return "launches"

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
