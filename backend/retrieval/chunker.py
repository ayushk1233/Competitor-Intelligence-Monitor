from typing import List


CHUNK_SIZE = 1200

CHUNK_OVERLAP = 200


def chunk_text(text: str) -> List[str]:

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end]

        chunks.append(chunk)

        start += (
            CHUNK_SIZE - CHUNK_OVERLAP
        )

    return chunks

if __name__ == "__main__":

    sample = "A" * 5000

    chunks = chunk_text(sample)

    print(f"Chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks):

        print(
            f"Chunk {i + 1}: "
            f"{len(chunk)} chars"
        )