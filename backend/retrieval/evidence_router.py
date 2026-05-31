# NOTE: Momentum is now exclusively derived from structured signals in signal_extractor.py.
# This router handles ONLY tone and ICP routing.

TONE_WEIGHTS = {
    # Technical / developer signals (existing — do NOT reduce)
    "developer": 3,
    "api": 3,
    "platform": 2,
    "enterprise": 1,
    "infrastructure": 3,
    "simple": 1,
    "scalable": 1,
    "modern": 1,
    "technical": 2,
    # HubSpot / CRM / SMB signals
    "marketing": 2,
    "sales": 2,
    "crm": 3,
    "customer platform": 3,
    "customer success": 2,
    "growth": 1,
    "business growth": 2,
    "revenue": 1,
    # Stripe / payments / fintech signals
    "payments": 2,
    "payment": 2,
    "commerce": 2,
    "checkout": 2,
    "fintech": 2,
    "financial": 1,
    "startup": 1,
    "agentic": 2,
    "partnership": 1,
}

ICP_WEIGHTS = {
    # Developer / technical / enterprise signals (existing — do NOT reduce)
    "developers": 3,
    "developer": 2,
    "engineering teams": 3,
    "engineering": 2,
    "api": 1,
    "platform": 1,
    "customers": 2,
    "businesses": 2,
    "enterprise": 1,
    "pricing": 0,
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
    # HubSpot / CRM / SMB signals
    "sales teams": 3,
    "revenue teams": 3,
    "customer support": 2,
    "customer service": 2,
    "customer success": 2,
    "crm": 3,
    "growing businesses": 2,
    "marketing": 2,
    "sales": 2,
    "customer platform": 2,
    # Stripe / payments / fintech signals
    "payments": 2,
    "payment": 2,
    "commerce": 2,
    "checkout": 2,
    "merchants": 3,
    "businesses of all sizes": 3,
    "internet economy": 2,
    "fintech": 2,
    "global businesses": 2,
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

    # Fallback: if routing returned nothing, use any chunks with a score > 0
    # sorted globally. Prevents reasoners from receiving empty context.
    for agent in ("tone", "icp"):
        if not routed[agent] and scored_by_agent[agent]:
            fallback = [
                chunk for score, chunk in sorted(
                    scored_by_agent[agent], key=lambda x: x[0], reverse=True
                )[:3]
                if score >= 0  # accept even score-0 chunks as last resort
            ]
            if fallback:
                routed[agent] = fallback
                print(f"[router] {agent} fallback activated ({len(fallback)} chunks)")

    # Issue 4: Routing audit
    print("\n===== ROUTING AUDIT =====")
    print(f"Tone chunks routed: {len(routed['tone'])}")
    print("TOP TONE CHUNKS:")
    for c in routed["tone"][:5]:
        print(f"  {repr(c[:150])}")
    print(f"\nICP chunks routed: {len(routed['icp'])}")
    print("TOP ICP CHUNKS:")
    for c in routed["icp"][:5]:
        print(f"  {repr(c[:150])}")
    print("=" * 25)

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