MOMENTUM_KEYWORDS = [

    "launch",
    "release",
    "roadmap",
    "hiring",
    "jobs",
    "careers",
    "AI",
    "expansion",
    "announce"
]

TONE_KEYWORDS = [

    "developer",
    "platform",
    "enterprise",
    "infrastructure",
    "simple",
    "scalable",
    "modern",
    "technical"
]

ICP_KEYWORDS = [

    "customers",
    "teams",
    "enterprise",
    "developers",
    "businesses",
    "pricing",
    "organizations"
]

def score_chunk(

    chunk: str,

    keywords: list[str]
):

    lower = chunk.lower()

    score = 0

    for keyword in keywords:

        if keyword in lower:

            score += 1

    return score

def route_evidence(
    chunks: list[str]
):

    routed = {}

    agent_configs = {

        "momentum": MOMENTUM_KEYWORDS,

        "tone": TONE_KEYWORDS,

        "icp": ICP_KEYWORDS
    }

    for (

        agent,

        keywords

    ) in agent_configs.items():

        scored_chunks = []

        for chunk in chunks:

            score = score_chunk(

                chunk,

                keywords
            )

            scored_chunks.append(

                (
                    score,
                    chunk
                )
            )

        # -------------------------
        # Sort by relevance
        # -------------------------

        scored_chunks.sort(

            reverse=True,

            key=lambda x: x[0]
        )

        # -------------------------
        # Keep top evidence
        # -------------------------

        top_chunks = [

            chunk

            for score, chunk

            in scored_chunks[:8]

            if score > 0
        ]

        # -------------------------
        # Fallback:
        # preserve some diversity
        # -------------------------

        if len(top_chunks) < 3:

            top_chunks.extend(

                chunks[:3]
            )

        routed[agent] = top_chunks

    return routed

if __name__ == "__main__":

    chunks = [

        "We launched new AI agents.",

        "Developer APIs for scalable infrastructure.",

        "Pricing plans for growing teams.",

        "We are hiring AI engineers.",

        "Simple tools for small startups."
    ]

    routed = route_evidence(
        chunks
    )

    from pprint import pprint

    pprint(routed)