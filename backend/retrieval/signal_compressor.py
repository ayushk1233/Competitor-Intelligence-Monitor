from collections import defaultdict


MAX_SIGNALS_PER_TYPE = 3


def compress_signals(
    signals: dict
):

    compressed = {}

    for (
        signal_type,
        evidence_list
    ) in signals.items():

        unique = []

        seen = set()

        for evidence in evidence_list:

            normalized = (
                evidence.lower().strip()
            )

            if normalized in seen:
                continue

            seen.add(normalized)

            unique.append(evidence)

        compressed[signal_type] = (
            unique[
                :MAX_SIGNALS_PER_TYPE
            ]
        )

    return compressed

if __name__ == "__main__":

    sample = {

        "ai_initiatives": [

            "Introducing our AI platform.",

            "Introducing our AI platform.",

            "New AI agent release."
        ]
    }

    compressed = compress_signals(
        sample
    )

    print(compressed)