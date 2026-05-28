from typing import List, Tuple

from backend.retrieval.chunker import (
    semantic_chunk
)

from backend.retrieval.signal_scorer import (
    score_text_signal
)

from backend.retrieval.semantic_router import (
    detect_page_weight
)


def rank_text_chunks(
    text: str,
    page_url: str
) -> List[Tuple[str, int]]:

    chunks = semantic_chunk(text)

    print(
        f"[ranking] Input chunks: {len(chunks)}"
    )

    scored_chunks = []

    page_weight = detect_page_weight(
        page_url
    )

    for chunk in chunks:

        signal_score = score_text_signal(
            chunk
        )

        score = (
            signal_score
            +
            page_weight
        )

        scored_chunks.append(
            (chunk, score)
        )

    scored_chunks.sort(
        key=lambda x: x[1],
        reverse=True
    )

    print(
        f"[ranking] Ranked chunks: {len(scored_chunks)}"
    )

    return scored_chunks

if __name__ == "__main__":

    sample = """
    Welcome to our company homepage.

    We are rapidly hiring AI engineers
    to expand our developer platform.

    Introducing our new AI agent system.

    Contact us for more details.
    """

    ranked = rank_text_chunks(sample)

    for i, (chunk, score) in enumerate(ranked):

        print(
            f"\nRank {i + 1}"
        )

        print(f"Score: {score}")

        print(chunk[:200])