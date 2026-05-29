import asyncio

from backend.reasoning.momentum_reasoner import (
    analyze_momentum
)

from backend.reasoning.tone_reasoner import (
    analyze_tone
)

from backend.reasoning.icp_reasoner import (
    analyze_icp
)

from backend.reasoning.synthesis_reasoner import (
    synthesize_intelligence
)

from backend.retrieval.evidence_router import (
    route_evidence
)

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
            if not any(pat in ev.lower() for pat in HISTORICAL_MOMENTUM_PATTERNS):
                clean_list.append(ev)
        if clean_list:
            sanitized[category] = clean_list
    return sanitized

async def run_intelligence_pipeline(
    chunks: list[str],
    signals: dict = None
):

    print(f"[orchestrator] Type received: {type(chunks)}")
    if isinstance(chunks, list) and chunks:
        print(f"[orchestrator] First chunk preview: {repr(chunks[0][:200])}")
    elif isinstance(chunks, str):
        print(f"[orchestrator] String preview: {repr(chunks[:200])}")

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
        return [
            c
            for c in chunk_list
            if not any(
                bad in c.lower()
                for bad in BAD
            )
        ]

    routed["momentum"] = filter_historical_chunks(routed["momentum"])

    if signals:
        sanitized_signals = sanitize_momentum_evidence(signals)
        momentum_context = "MOMENTUM SIGNALS\n\n"
        for category, evidence_list in sanitized_signals.items():
            if evidence_list:
                momentum_context += f"--- {category.replace('_', ' ').upper()} ---\n"
                for ev in evidence_list:
                    momentum_context += f"- {ev}\n"
                momentum_context += "\n"
    else:
        momentum_context = "\n\n".join(
            routed["momentum"]
        )

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

        icp_analysis=icp_result
    )

    import os
    import time

    def log_agent_output(agent_name: str, output: str):
        log_dir = "logs/agent_outputs"
        os.makedirs(log_dir, exist_ok=True)
        timestamp = int(time.time())
        file_path = os.path.join(log_dir, f"{agent_name}_{timestamp}.txt")
        try:
            with open(file_path, "w") as f:
                f.write(str(output))
        except Exception as e:
            print(f"Failed to write agent log: {e}")

    log_agent_output("momentum", momentum_result)
    log_agent_output("tone", tone_result)
    log_agent_output("icp", icp_result)
    log_agent_output("synthesis", final_result)

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