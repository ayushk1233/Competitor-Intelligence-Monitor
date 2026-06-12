import asyncio

from backend.reasoning.icp_reasoner import analyze_icp
from backend.reasoning.momentum_reasoner import analyze_momentum
from backend.reasoning.synthesis_reasoner import synthesize_intelligence
from backend.reasoning.tone_reasoner import analyze_tone
from backend.retrieval.evidence_router import route_evidence


def is_real_momentum_signal(text: str) -> bool:
    """Accepts launches, shipping velocity, adoption, partnerships, hiring, and funding."""
    EVENT_TERMS = [
        "announced", "launches", "launched", "released", "partnership",
        "partnered", "acquisition", "acquired", "hiring", "expands",
        "expansion", "investment", "funding", "award", "breakthrough",
        "introduces", "introducing",
        # Adoption terms must survive
        "engineers", "adoption", "users", "growing from", "% of", "thousands",
        "millions", "used by",
        # Shipping velocity terms
        "published", "changelog", "update", "new feature", "added support",
        "improvement", "now available"
    ]
    return any(t in text.lower() for t in EVENT_TERMS)

# Keep old name as alias for backwards compatibility
is_real_momentum_event = is_real_momentum_signal

def is_marketing_copy(text: str) -> bool:
    MARKETING_PHRASES = [
        "next-generation ai", "optimized for scale", "trusted ai",
        "ai productivity", "modern infrastructure", "future-proof",
        "hybrid cloud", "enterprise ai"
    ]
    return any(t in text.lower() for t in MARKETING_PHRASES)

def sanitize_momentum_evidence(signals_dict: dict) -> dict:
    if not signals_dict:
        return signals_dict
        
    HISTORICAL_MOMENTUM_PATTERNS = [
        "years ago",
        "first released",
        "over the years",
        "founded",
        "origin story",
        "started the company",
        "27 years",
        "23 years",
        "decades"
    ]
    
    sanitized = {}
    for category, ev_list in signals_dict.items():
        clean_list = []
        for ev in ev_list:
            if any(pat in ev.lower() for pat in HISTORICAL_MOMENTUM_PATTERNS):
                continue
            if is_marketing_copy(ev) and not is_real_momentum_signal(ev):
                continue
            # Only validate real-event types for launch; always pass adoption/velocity
            if category in ("launch_signals",) and not is_real_momentum_signal(ev):
                continue
            clean_list.append(ev)
        if clean_list:
            sanitized[category] = clean_list
    return sanitized

async def run_intelligence_pipeline(
    chunks: list[str],
    signals: dict = None,
    validation: dict = None
):

    # -----------------------------------
    # Run specialist agents concurrently
    # -----------------------------------

    routed = route_evidence(
        chunks
    )

    def filter_historical_chunks(chunk_list):
        BAD = [
            "years ago",
            "first released",
            "over the years",
            "23 years",
            "27 years",
            "founded",
            "origin story"
        ]
        valid_chunks = []
        for c in chunk_list:
            if any(bad in c.lower() for bad in BAD):
                continue
            if is_marketing_copy(c) and not is_real_momentum_signal(c):
                continue
            valid_chunks.append(c)
        return valid_chunks

    if "momentum" in routed:
        routed["momentum"] = filter_historical_chunks(routed["momentum"])

    if signals:
        sanitized_signals = sanitize_momentum_evidence(signals)

        # Build structured-only context — NO raw chunks reach momentum LLM
        momentum_context = "MOMENTUM SIGNALS\n\n"
        momentum_context += "Only the following structured signals are available.\n"
        momentum_context += "Do NOT infer additional evidence beyond what is listed below.\n\n"

        MOMENTUM_CATEGORIES = [
            "launch_signals",
            "shipping_velocity_signals",
            "adoption_signals",
            "hiring_signals",
            "partnership_signals",
        ]
        total_evidence = 0
        for category in MOMENTUM_CATEGORIES:
            evidence_list = sanitized_signals.get(category, [])
            total_evidence += len(evidence_list)
            category_label = category.replace("_", " ").upper()
            if evidence_list:
                momentum_context += f"--- {category_label} ---\n"
                for ev in evidence_list:
                    momentum_context += f"- {ev}\n"
                momentum_context += "\n"
            else:
                momentum_context += f"--- {category_label} ---\n"
                momentum_context += "(none)\n\n"

        momentum_context += f"Total unique evidence items: {total_evidence}\n"
    else:
        # No structured signals provided — momentum context is empty
        # The LLM will score conservatively with no evidence
        momentum_context = "MOMENTUM SIGNALS\n\nNo structured signals available.\nReturn momentum_score: 1\n"

    tone_context = "\n\n".join(
        routed["tone"]
    )

    icp_context = "\n\n".join(
        routed["icp"]
    )

    (
        momentum_result,

        tone_result,

        icp_result

    ) = await asyncio.gather(

        analyze_momentum(momentum_context),

        analyze_tone(tone_context),

        analyze_icp(icp_context)
    )

    # -----------------------------------
    # Strategic synthesis
    # -----------------------------------
    
    full_context_str = "\n\n".join(chunks)

    final_result = await synthesize_intelligence(

        context=full_context_str,

        momentum_analysis=momentum_result,

        tone_analysis=tone_result,

        icp_analysis=icp_result,

        validation=validation
    )

    return {

        "momentum": momentum_result,

        "tone": tone_result,

        "icp": icp_result,

        "final": final_result
    }

async def main():

    sample_chunks = [
        "The company launched multiple AI products and is rapidly hiring enterprise engineers.",
        "Their developer platform provides scalable APIs for enterprise customers."
    ]

    result = await run_intelligence_pipeline(
        sample_chunks
    )

    print(result["final"])


if __name__ == "__main__":

    asyncio.run(main())