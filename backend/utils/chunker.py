from backend.config import get_settings

settings = get_settings()


def chunk_text(text: str, max_tokens: int = None) -> list[str]:
    """
    Split text into chunks that fit within Claude/Gemini context limits.
    Uses word count as a token proxy (1 token ≈ 0.75 words).
    """
    if max_tokens is None:
        max_tokens = settings.max_tokens_per_chunk

    # Convert token limit to approximate word limit
    max_words = int(max_tokens * 0.75)

    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0

    for word in words:
        current_chunk.append(word)
        current_count += 1

        if current_count >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_count = 0

    # Append any remaining words
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def merge_page_contents(pages: list[dict], max_tokens: int = None) -> str:
    """
    Merge multiple pages into a single string that fits the token budget.
    Priority order: homepage > pricing > about > blog > careers.
    Each page section is labelled so Claude knows what it's reading.
    """
    if max_tokens is None:
        max_tokens = settings.max_tokens_per_chunk

    priority = ["homepage", "pricing", "about", "blog", "careers"]

    # Sort pages by priority
    sorted_pages = sorted(
        pages,
        key=lambda p: priority.index(p["page_type"])
        if p["page_type"] in priority else 99
    )

    max_words = int(max_tokens * 0.75)
    merged = []
    total_words = 0

    for page in sorted_pages:
        if not page.get("content"):
            continue

        label = f"\n\n=== {page['page_type'].upper()} PAGE ({page['url']}) ===\n"
        content = page["content"]

        # How many words does this page add?
        page_words = len(content.split())
        label_words = len(label.split())

        if total_words + label_words + page_words > max_words:
            # Trim this page to whatever space is left
            remaining = max_words - total_words - label_words
            if remaining > 100:  # Only add if there's meaningful space left
                trimmed = " ".join(content.split()[:remaining])
                merged.append(label + trimmed)
            break

        merged.append(label + content)
        total_words += label_words + page_words

    return "\n".join(merged)