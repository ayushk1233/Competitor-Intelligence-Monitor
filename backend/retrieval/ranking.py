from typing import List, Tuple

from backend.retrieval.chunker import (
    chunk_text
)

from backend.retrieval.signal_scorer import (
    score_text_signal
)


def rank_text_chunks(
    text: str
) -> List[Tuple[str, int]]:

    chunks = chunk_text(text)

    scored_chunks = []

    for chunk in chunks:

        score = score_text_signal(
            chunk
        )

        scored_chunks.append(
            (chunk, score)
        )

    scored_chunks.sort(
        key=lambda x: x[1],
        reverse=True
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