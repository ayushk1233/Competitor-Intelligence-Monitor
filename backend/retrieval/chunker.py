import re

def semantic_chunk(
    text: str
):

    # -------------------------
    # Split by semantic breaks
    # -------------------------

    sections = re.split(

        r"\n\s*\n",

        text
    )

    chunks = []

    current_chunk = ""

    MAX_CHARS = 1200

    for section in sections:

        section = section.strip()

        if not section:

            continue

        # -------------------------
        # Keep semantic coherence
        # -------------------------

        if (

            len(current_chunk)
            + len(section)

            < MAX_CHARS
        ):

            current_chunk += (
                "\n\n" + section
            )

        else:

            if current_chunk:

                chunks.append(
                    current_chunk.strip()
                )

            current_chunk = section

    # -------------------------
    # Final chunk
    # -------------------------

    if current_chunk:

        chunks.append(
            current_chunk.strip()
        )

    print(f"[chunker] Produced {len(chunks)} chunks")

    for i, chunk in enumerate(chunks[:5]):

        print(f"\n--- Chunk {i+1} ---")

        print(chunk[:300])

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