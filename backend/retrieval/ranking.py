from typing import List, Tuple

from backend.retrieval.chunker import semantic_chunk
from backend.retrieval.semantic_router import detect_page_weight
from backend.retrieval.signal_scorer import score_text_signal


def is_semantically_similar(
    chunk_a: str,
    chunk_b: str
):

    words_a = set(
        chunk_a.lower().split()
    )

    words_b = set(
        chunk_b.lower().split()
    )

    overlap = len(
        words_a.intersection(words_b)
    )

    union = len(
        words_a.union(words_b)
    )

    if union == 0:
        return False

    similarity = overlap / union

    return similarity > 0.7


def rank_text_chunks(
    text: str,
    page_url: str
) -> List[Tuple[int, str]]:

    chunks = semantic_chunk(text)

    print(
        f"[ranking] Received {len(chunks)} chunks"
    )

    scored_chunks = []

    page_weight = detect_page_weight(
        page_url
    )

    NEGATIVE_PATTERNS = [
        "contact sales",
        "accept cookies",
        "cookie policy",
        "language",
        "privacy policy",
        "terms of service"
    ]

    for chunk in chunks:

        signal_score = score_text_signal(
            chunk
        )
        
        chunk_lower = chunk.lower()
        for pattern in NEGATIVE_PATTERNS:
            if pattern in chunk_lower:
                signal_score -= 5

        score = (
            signal_score
            +
            page_weight
        )

        scored_chunks.append(
            (score, chunk)
        )

    ranked = sorted(
        scored_chunks,
        key=lambda x: x[0],
        reverse=True
    )

    print("\n[ranking] Top Ranked Chunks")

    for score, chunk in ranked[:5]:

        print(f"\nScore: {score}")

        print(chunk[:300])

        print("-" * 40)

    # -----------------------------------
    # Semantic deduplication
    # -----------------------------------

    diverse_ranked = []

    for score, chunk in ranked:

        is_duplicate = False

        for _, existing_chunk in diverse_ranked:

            if is_semantically_similar(
                chunk,
                existing_chunk
            ):

                is_duplicate = True
                break

        if not is_duplicate:

            diverse_ranked.append(
                (score, chunk)
            )

    print(
        f"[ranking] Diverse chunks: {len(diverse_ranked)}"
    )

    for score, chunk in diverse_ranked[:5]:

        print("\n[ranking] Diverse Chunk")

        print(chunk[:300])

    return diverse_ranked

if __name__ == "__main__":

    sample = """
    Welcome to our company homepage.

    We are rapidly hiring AI engineers
    to expand our developer platform.

    Introducing our new AI agent system.

    Contact us for more details.
    """

    ranked = rank_text_chunks(sample)

    for i, (score, chunk) in enumerate(ranked):

        print(
            f"\nRank {i + 1}"
        )

        print(f"Score: {score}")

        print(chunk[:200])