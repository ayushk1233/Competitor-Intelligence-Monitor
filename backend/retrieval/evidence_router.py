# NOTE: Momentum is now exclusively derived from structured signals in signal_extractor.py.
# This router handles ONLY tone and ICP routing.

TONE_WEIGHTS = {
    "developer": 3,
    "api": 3,
    "platform": 2,
    "enterprise": 1,
    "infrastructure": 3,
    "simple": 1,
    "scalable": 1,
    "modern": 1,
    "technical": 2
}

ICP_WEIGHTS = {
    "developers": 3,
    "developer": 2,
    "engineering teams": 3,
    "engineering": 2,
    "api": 1,
    "platform": 1,
    "customers": 2,
    "businesses": 2,
    "enterprise": 1,
    "pricing": 1,
    "pro": 1,
    "enterprise plan": 3,
    "for teams": 3,
    "for business": 3,
    "organizations": 1,
    "startups": 2,
    "teams": 2,
    "project managers": 3,
    "small businesses": 3,
    "marketing teams": 3,
    "operations teams": 3,
    "agencies": 3,
    "founders": 3,
    "companies": 1,
    "per seat": 2,
    "per user": 2,
    "per month": 1,
    "free tier": 2,
    "self-serve": 2,
    "enterprise": 1,
    "for enterprise": 3
}

def score_chunk(
    chunk: str,
    weights: dict[str, int],
    category_name: str = "UNKNOWN"
):
    lower = chunk.lower()
    score = 0

    for keyword, weight in weights.items():
        if keyword in lower:
            score += weight
            print(f"{category_name.upper()} MATCH: {keyword} (+{weight})")

    return score

def route_evidence(
    chunks: list[str]
):

    routed = {
        "tone": [],
        "icp": []
    }
    
    # Store tuples of (score, chunk) for sorting later
    scored_by_agent = {
        "tone": [],
        "icp": []
    }

    for chunk in chunks:
        tone_score = score_chunk(chunk, TONE_WEIGHTS, "TONE")
        icp_score = score_chunk(chunk, ICP_WEIGHTS, "ICP")
        
        print("\nCHUNK:")
        print(chunk[:200].strip() + ("..." if len(chunk) > 200 else ""))
        print(f"ICP SCORE: {icp_score}")
        print(f"TONE SCORE: {tone_score}")

        scored_by_agent["tone"].append((tone_score, chunk))
        scored_by_agent["icp"].append((icp_score, chunk))

    for agent, scored_chunks in scored_by_agent.items():
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
        # Fallback: Removed.
        # Blindly appending chunks[:3] was polluting the context
        # and causing evidence leakage.
        # -------------------------

        routed[agent] = top_chunks

    print("\nFINAL ICP:")
    for c in routed["icp"]:
        print(c)

    print("\nFINAL TONE:")
    for c in routed["tone"]:
        print(c)

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