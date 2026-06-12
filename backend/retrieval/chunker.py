import re

from backend.utils.cleaner import clean_page_content


def semantic_chunk(text):

    # ---------------------------------------------------
    # Jina AI reader delivers content as a single long
    # line with '\n' (not '\n\n') separators. A pure
    # paragraph split produces only 1-2 chunks.
    # Strategy:
    #   1. Split on any double-newline OR single newline
    #      followed by content (handles both formats).
    #   2. Accumulate up to MAX_CHARS per chunk so that
    #      we get 10-30 chunks from a full page.
    # ---------------------------------------------------

    # Strip cookie banners before chunking
    text = clean_page_content(text)

    MAX_CHARS = 800  # smaller ceiling → more chunks → better ranking diversity

    # Split by paragraph blocks (\n\n+) or Markdown headings (# )
    # This preserves semantic coherence, narrative structure, and
    # evidence grouping, replacing the destructive sentence splitting.
    lines = re.split(r"\n\n+|(?=\n?#\s)", text)

    chunks = []
    current = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if len(current) + len(line) < MAX_CHARS:
            current += " " + line if current else line

        else:
            if current.strip():
                chunks.append(current.strip())
            current = line

    if current.strip():
        chunks.append(current.strip())

    # Drop trivially short fragments
    chunks = [c for c in chunks if len(c) > 40]

    print(
        f"[chunker] Produced {len(chunks)} chunks"
    )

    for i, chunk in enumerate(chunks[:5]):

        print(f"\n[chunker] Chunk {i+1}")

        print(chunk[:400])

        print("-" * 40)

    return chunks

if __name__ == "__main__":

    sample = """

Welcome to our AI platform.

We help developers build
scalable infrastructure.


We are launching
new coding agents.

Hiring globally for AI engineers.


Enterprise customers can use
advanced governance features.

"""

    chunks = semantic_chunk(
        sample
    )

    for i, chunk in enumerate(chunks):

        print(f"\n--- Chunk {i+1} ---\n")

        print(chunk)