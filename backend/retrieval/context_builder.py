from typing import List

from backend.retrieval.ranking import (
    rank_text_chunks
)


MAX_CONTEXT_CHARS = 12000
MAX_CHUNKS_PER_PAGE = 2


def build_ranked_context(
    pages: List[str]
) -> str:

    all_ranked_chunks = []

    # -----------------------------------
    # Rank chunks from all pages
    # -----------------------------------

    for page in pages:

        ranked_chunks = rank_text_chunks(
            page
        )

        all_ranked_chunks.extend(
            ranked_chunks[:MAX_CHUNKS_PER_PAGE]
        )

    # -----------------------------------
    # Global ranking
    # -----------------------------------

    all_ranked_chunks.sort(
        key=lambda x: x[1],
        reverse=True
    )

    # -----------------------------------
    # Build final context
    # -----------------------------------

    final_chunks = []

    current_size = 0
    used_phrases = set()

    for chunk, score in all_ranked_chunks:

        fingerprint = chunk[:200].strip()
        if fingerprint in used_phrases:
            continue

        chunk_size = len(chunk)

        if (
            current_size + chunk_size
            > MAX_CONTEXT_CHARS
        ):
            break

        final_chunks.append(chunk)

        current_size += chunk_size
        used_phrases.add(fingerprint)

    return "\n\n".join(final_chunks)

if __name__ == "__main__":

    pages = [

        """
        Welcome to homepage.
        Basic company info.
        """,

        """
        Introducing our new AI platform.
        We are rapidly hiring engineers
        to expand our developer API.
        """
    ]

    context = build_ranked_context(
        pages
    )

    print(context)