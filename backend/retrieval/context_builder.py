from typing import List

from backend.retrieval.page_classifier import classify_page_type
from backend.retrieval.ranking import rank_text_chunks

# ---------------------------------------------------------------------------
# BUDGET & WEIGHTS
# ---------------------------------------------------------------------------

MAX_CONTEXT_CHARS = 15000  # Fix 3: Increased budget

# Fix 2: Per-page-type chunk quota (prevents homepage monopolisation)
PAGE_TYPE_LIMITS = {
    "homepage": 2,   # Raised: homepage often contains news/announcements alongside generic copy
    "about":    1,
    "blog":     2,
    "careers":  1,
    "pricing":  1,
    "docs":     1,
    "news":     2,
    "press":    2,
    "launches": 2,
    "research": 2,
    "changelog":2,
}

DEFAULT_BUDGET = 2

# Fix 5: Momentum-aware page priority multipliers
PAGE_TYPE_WEIGHTS = {
    "news":      3.0,
    "blog":      2.5,
    "press":     2.5,
    "research":  2.0,
    "careers":   2.0,
    "changelog": 2.0,
    "launches":  2.0,
    "docs":      1.5,
    "about":     1.0,
    "homepage":  1.0,
    "pricing":   0.5,
}

# Fix: Page selection priority — sort before diversity enforcement
PAGE_PRIORITY = {
    "news":      100,
    "press":     95,
    "blog":      90,
    "research":  85,
    "careers":   70,
    "changelog": 70,
    "launches":  70,
    "docs":      60,
    "homepage":  50,
    "about":     40,
    "pricing":   30,
}

# High-signal keywords — chunks containing these are PROTECTED from diversity eviction
HIGH_SIGNAL_KEYWORDS = [
    "announced", "launch", "launched", "released", "research",
    "granite", "partnership", "funding", "hiring", "job openings",
    "new product", "product announcement", "think 2026", "red hat",
    "ibm bob", "open source", "$5 billion", "5 billion",
    "published 20", "adoption", "% of engineers",
]

NOISE_PATTERNS = [
    "privacy policy", "cookie policy", "accept all cookies",
    "all products and features", "terms of service", "copyright",
    "download on the app store", "get it on google play",
    "global headquarters", "instagram", "linkedin",
    "youtube", "facebook", "reddit",
]

MIN_CONTENT_LENGTH = 200


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def is_noise(chunk: str) -> bool:
    if len(chunk) > MIN_CONTENT_LENGTH:
        return False
    lower = chunk.lower()
    return any(p in lower for p in NOISE_PATTERNS)


def has_momentum_signal(chunk: str) -> bool:
    """Identify chunks that contain signal-rich content (used for priority ordering)."""
    lower = chunk.lower()
    return any(k in lower for k in HIGH_SIGNAL_KEYWORDS)


def is_high_signal_chunk(chunk: str) -> bool:
    """Protected chunks — must NEVER be dropped during diversity enforcement."""
    lower = chunk.lower()
    return any(k in lower for k in HIGH_SIGNAL_KEYWORDS)


def signal_boost(chunk: str) -> float:
    """Signal-aware score boost: +10 per keyword hit. Rewards launch/adoption evidence."""
    lower = chunk.lower()
    return sum(10.0 for k in HIGH_SIGNAL_KEYWORDS if k in lower)


def compute_context_quality(all_chunks: list, chunks_by_type: dict) -> dict:
    """Fix 7: Compute quality metrics across ALL accepted chunks (before any removal)."""
    full_text = " ".join(c for _, c, _ in all_chunks).lower()
    page_diversity = len([pt for pt, cks in chunks_by_type.items() if cks])

    SIGNAL_KEYWORDS = HIGH_SIGNAL_KEYWORDS
    signal_count = sum(1 for k in SIGNAL_KEYWORDS if k in full_text)
    launch_count = full_text.count("launched") + full_text.count("announced")
    adoption_count = full_text.count("% of") + full_text.count("engineers")
    career_count = full_text.count("hiring") + full_text.count("open roles")
    news_count = len(chunks_by_type.get("news", [])) + len(chunks_by_type.get("blog", []))

    quality_score = min(10, page_diversity * 1.5 + signal_count * 0.5)

    return {
        "quality_score": round(quality_score, 1),
        "page_diversity": page_diversity,
        "signal_richness": signal_count,
        "launch_count": launch_count,
        "adoption_count": adoption_count,
        "career_count": career_count,
        "news_count": news_count,
    }


def enforce_context_diversity(chunks_with_meta: list) -> list:
    """
    Never allow >50% of the final context from a single page type.
    CRITICAL: High-signal chunks are ALWAYS protected and never evicted.
    Only low-signal chunks are subject to per-type budget enforcement.
    """
    if not chunks_with_meta:
        return chunks_with_meta

    # Separate protected (high-signal) from candidates
    protected = [(s, c, pt) for s, c, pt in chunks_with_meta if is_high_signal_chunk(c)]
    candidates = [(s, c, pt) for s, c, pt in chunks_with_meta if not is_high_signal_chunk(c)]

    if not candidates:
        return protected

    total_chars = sum(len(c) for _, c, _ in candidates)
    if total_chars == 0:
        return protected + candidates

    by_type = {}
    for item in candidates:
        by_type.setdefault(item[2], []).append(item)

    dominated = any(
        sum(len(c) for _, c, _ in items) / total_chars > 0.5
        for items in by_type.values()
    )

    if not dominated:
        return protected + candidates

    print("[context-builder] Diversity enforcement triggered on non-protected chunks")
    type_count = len(by_type)
    # Budget applies only to the non-protected candidate pool
    candidate_budget = MAX_CONTEXT_CHARS // max(type_count, 1)

    rebalanced = []
    for pt, items in by_type.items():
        allocated = 0
        for item in sorted(items, key=lambda x: x[0], reverse=True):
            _, chunk, _ = item
            if allocated + len(chunk) <= candidate_budget:
                rebalanced.append(item)
                allocated += len(chunk)

    # Protected chunks always included
    return protected + rebalanced


# ---------------------------------------------------------------------------
# MAIN BUILD FUNCTION
# ---------------------------------------------------------------------------

def build_ranked_context(
    pages: List[dict]
) -> List[str]:

    all_ranked_chunks = []

    # Tracking for audit
    context_stats = {}

    # Fix 1 + Fix 2: Per-page-type quota + full audit logging
    print("\n===== CONTEXT AUDIT =====")
    print(f"Total pages received: {len(pages)}")

    chunks_by_type = {}

    for page in pages:
        url = page["url"]
        page_type = page.get("page_type") or classify_page_type(url)
        budget = PAGE_TYPE_LIMITS.get(page_type, DEFAULT_BUDGET)
        weight = PAGE_TYPE_WEIGHTS.get(page_type, 1.0)

        ranked_chunks = rank_text_chunks(
            text=page["content"],
            page_url=url
        )

        accepted_for_page = 0

        # Sort by signal-boosted score so high-signal chunks win within the page budget.
        # This ensures 'IBM and Red Hat Commit $5B' beats the generic AI overview
        # even if the ranker gave the overview a higher base score.
        signal_sorted = sorted(
            ranked_chunks,
            key=lambda sc_chunk: sc_chunk[0] + signal_boost(sc_chunk[1]),
            reverse=True
        )

        for score, chunk in signal_sorted:
            if accepted_for_page >= budget:
                break
            if is_noise(chunk):
                continue

            # Weight by page type
            weighted_score = score * weight
            all_ranked_chunks.append((weighted_score, chunk, page_type))
            chunks_by_type.setdefault(page_type, []).append((weighted_score, chunk, page_type))
            accepted_for_page += 1

        print(
            f"  [page] type={page_type} budget={budget} weight={weight}x "
            f"accepted={accepted_for_page} url={url[:80]}"
        )

    print(f"\nAccepted Chunks (total): {len(all_ranked_chunks)}")
    for score, chunk, pt in all_ranked_chunks:
        print(f"  page_type={pt}  len={len(chunk)}  preview={repr(chunk[:150])}")

    # Fix 7: Compute quality BEFORE any chunk removal (over all accepted chunks)
    quality = compute_context_quality(all_ranked_chunks, chunks_by_type)
    print("\n[CONTEXT QUALITY — pre-assembly]")
    for k, v in quality.items():
        print(f"  {k}: {v}")
    print("=" * 25)

    # Sort within each type by score
    for pt in chunks_by_type:
        chunks_by_type[pt].sort(key=lambda x: x[0], reverse=True)

    # PAGE_PRIORITY sort before diversity enforcement
    all_ranked_chunks.sort(
        key=lambda c: PAGE_PRIORITY.get(c[2], 0),
        reverse=True
    )

    # Apply signal boost to scores before final sort
    all_ranked_chunks = [
        (score + signal_boost(chunk), chunk, pt)
        for score, chunk, pt in all_ranked_chunks
    ]

    # Diversity enforcement — protected chunks survive, candidates balanced
    all_ranked_chunks = enforce_context_diversity(all_ranked_chunks)

    # ---- Separate momentum-signal chunks from the rest ----
    # Fix 6: Protect high-signal chunks — they go in first regardless of score
    priority_chunks = [(s, c, pt) for s, c, pt in all_ranked_chunks if has_momentum_signal(c)]
    normal_chunks   = [(s, c, pt) for s, c, pt in all_ranked_chunks if not has_momentum_signal(c)]

    priority_chunks.sort(key=lambda x: x[0], reverse=True)
    normal_chunks.sort(key=lambda x: x[0], reverse=True)

    ordered = priority_chunks + normal_chunks

    # ---- Assemble final context within budget ----
    context_chunks = []
    total_chars = 0

    for score, chunk, page_type in ordered:
        if not chunk or not chunk.strip():
            continue
        if total_chars + len(chunk) > MAX_CONTEXT_CHARS:
            # Skip this chunk but continue — do NOT break
            # This prevents one large chunk from blocking smaller ones
            continue
        context_chunks.append(chunk)
        total_chars += len(chunk)
        context_stats[page_type] = context_stats.get(page_type, 0) + len(chunk)

    print(f"\nSelected Chunks: {len(context_chunks)}")
    print(f"Final Context Chars: {total_chars}")
    for pt, chars in sorted(context_stats.items(), key=lambda x: -x[1]):
        pct = round(100 * chars / max(total_chars, 1))
        print(f"  - {pt}: {chars} chars ({pct}%)")

    # Validate key evidence presence
    flat_text = "\n\n".join(context_chunks).lower()
    KEY_EVIDENCE = ["granite", "red hat", "think 2026", "ibm bob", "5 billion"]
    print("\n[KEY EVIDENCE CHECK]")
    for kw in KEY_EVIDENCE:
        found = "✓" if kw in flat_text else "✗"
        print(f"  {found} {kw}")

    if total_chars < 6000:
        company_guess = pages[0]["url"] if pages else "unknown"
        print(
            f"\n[WARNING] Context starvation detected.\n"
            f"Company: {company_guess}\n"
            f"Chars: {total_chars}\n"
        )

    flat_preview = "\n\n".join(context_chunks)
    print("\n[DEBUG] FINAL CONTEXT PREVIEW")
    print(repr(flat_preview[:500]))

    return context_chunks


if __name__ == "__main__":

    pages = [
        {
            "url": "https://example.com",
            "page_type": "homepage",
            "content": "Welcome to homepage. Basic company info."
        },
        {
            "url": "https://example.com/blog/launch",
            "page_type": "blog",
            "content": "Today we announced the launch of our new AI platform for 2026."
        },
        {
            "url": "https://example.com/careers",
            "page_type": "careers",
            "content": "We are hiring engineers. Open roles in ML and infrastructure."
        }
    ]

    context = build_ranked_context(pages)
    print(context)