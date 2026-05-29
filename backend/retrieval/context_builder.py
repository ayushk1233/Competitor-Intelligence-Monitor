from typing import List

from backend.retrieval.ranking import (
    rank_text_chunks
)

from backend.retrieval.page_classifier import (
    classify_page_type
)


MAX_CONTEXT_CHARS = 12000

# -----------------------------------
# Max chunks per page type
# -----------------------------------

PAGE_TYPE_BUDGET = {
    "homepage": 3,
    "docs":     2,
    "careers":  2,
    "pricing":  2,
    "launches": 2,
}

DEFAULT_BUDGET = 2


# -----------------------------------
# Noise filter
# -----------------------------------

NOISE_PATTERNS = [
    "privacy policy",
    "cookie policy",
    "accept all cookies",
    "all products and features",
    "terms of service",
    "copyright",
    "download on the app store",
    "get it on google play",
    "global headquarters",
    "instagram",
    "linkedin",
    "youtube",
    "facebook",
    "reddit",
]


# Chunks shorter than this are likely pure navigation/footer noise
MIN_CONTENT_LENGTH = 200


def is_noise(chunk: str) -> bool:

    # Never discard substantive content blocks —
    # large chunks may contain social links inside
    # real product prose. Only filter tiny nav/footer
    # fragments that are mostly boilerplate.
    if len(chunk) > MIN_CONTENT_LENGTH:
        return False

    lower = chunk.lower()

    for pattern in NOISE_PATTERNS:
        if pattern in lower:
            return True

    return False


def build_ranked_context(
    pages: List[dict]
) -> List[str]:

    all_ranked_chunks = []
    
    # -----------------------------------
    # Retrieval Audit Tracking
    # -----------------------------------
    context_stats = {
        "homepage": 0,
        "about": 0,
        "pricing": 0,
        "blog": 0,
        "careers": 0,
        "launches": 0,
        "docs": 0,
        "other": 0
    }

    # -----------------------------------
    # Balanced retrieval per page type
    # -----------------------------------

    for page in pages:

        url = page["url"]

        # Use stored page_type or classify from URL
        page_type = page.get("page_type") or classify_page_type(url)

        budget = PAGE_TYPE_BUDGET.get(
            page_type, DEFAULT_BUDGET
        )

        ranked_chunks = rank_text_chunks(
            text=page["content"],
            page_url=url
        )

        accepted_for_page = 0

        for score, chunk in ranked_chunks:

            if accepted_for_page >= budget:
                break

            if is_noise(chunk):
                continue

            all_ranked_chunks.append(
                (score, chunk, page_type)
            )

            accepted_for_page += 1
            
        print(
            f"[page-audit] type={page_type} url={url} "
            f"chars={len(page['content'])} chunks_accepted={accepted_for_page}"
        )

    # -----------------------------------
    # Group by Page Type & Enforce Diversity
    # -----------------------------------
    
    chunks_by_type = {}
    for item in all_ranked_chunks:
        pt = item[2]
        if pt not in chunks_by_type:
            chunks_by_type[pt] = []
        chunks_by_type[pt].append(item)
        
    for pt in chunks_by_type:
        chunks_by_type[pt].sort(key=lambda x: x[0], reverse=True)

    diverse_chunks = []
    
    # 1. Take top 2 from each page type to guarantee diversity
    for pt, chunks in chunks_by_type.items():
        diverse_chunks.extend(chunks[:2])
        
    # 2. Add remaining chunks, sorted globally by score, if we have leftover budget
    remaining_chunks = []
    for pt, chunks in chunks_by_type.items():
        remaining_chunks.extend(chunks[2:])
        
    remaining_chunks.sort(key=lambda x: x[0], reverse=True)
    
    final_ordered_chunks = diverse_chunks + remaining_chunks

    print(
        f"\n[context-builder] Total chunks after balanced retrieval: "
        f"{len(final_ordered_chunks)}"
    )

    # -----------------------------------
    # Build final context list
    # -----------------------------------

    print("\n[DEBUG] ACCEPTED CHUNKS")

    for score, chunk, pt in final_ordered_chunks:
        print(f"  type={type(chunk).__name__}  len={len(chunk)}  page_type={pt}")
        print(f"  preview: {repr(chunk[:200])}")

    context_chunks = []
    total_chars = 0

    for score, chunk, page_type in final_ordered_chunks:
        if not chunk or not chunk.strip():
            continue

        # Chunks are already semantically sized (~800 chars),
        # so we can just add them intact until we hit the context ceiling.
        if total_chars + len(chunk) > MAX_CONTEXT_CHARS:
            break

        context_chunks.append(chunk)
        total_chars += len(chunk)
        
        # Track stats
        stat_key = page_type if page_type in context_stats else "other"
        context_stats[stat_key] += len(chunk)

    print(
        f"\n[context-builder] Final chars: {total_chars}"
    )
    
    for pt, chars in context_stats.items():
        if chars > 0:
            print(f"  - {pt}: {chars} chars")

    if total_chars < 6000:
        company_guess = pages[0]["url"] if pages else "unknown"
        print(
            f"\n[WARNING]\n"
            f"Context starvation detected.\n"
            f"Company: {company_guess}\n"
            f"Chars: {total_chars}\n"
            f"Page Types: {context_stats}"
        )

    print("\n[DEBUG] FINAL CONTEXT")
    
    flat_context_preview = "\n\n".join(context_chunks)
    print(repr(flat_context_preview[:500]))
    
    # -----------------------------------
    # Phrase Audit
    # -----------------------------------
    from collections import Counter
    import re
    words = re.findall(r'\b[a-z]{3,}\b', flat_context_preview.lower())
    phrases = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
    top_phrases = Counter(phrases).most_common(10)
    print("\n[DEBUG] TOP PHRASES IN CONTEXT:")
    for phrase, count in top_phrases:
        if count > 2:
            print(f"  {phrase}: {count}")

    return context_chunks

if __name__ == "__main__":

    pages = [
        {
            "url": "https://example.com",
            "page_type": "homepage",
            "content": """
            Welcome to homepage.
            Basic company info.
            """
        },
        {
            "url": "https://example.com/about",
            "page_type": "about",
            "content": """
            Introducing our new AI platform.
            We are rapidly hiring engineers
            to expand our developer API.
            """
        }
    ]

    context = build_ranked_context(
        pages
    )

    print(context)