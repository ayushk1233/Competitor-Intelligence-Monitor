import asyncio

from backend.reasoning.icp_reasoner import analyze_icp
from backend.reasoning.momentum_reasoner import analyze_momentum
from backend.reasoning.synthesis_reasoner import synthesize_intelligence
from backend.reasoning.tone_reasoner import analyze_tone
from backend.reasoning.strategy_reasoner import analyze_strategy
from backend.reasoning.archetype_scoring import score_archetypes
from backend.reasoning.evidence_registry import EvidenceRegistry
from backend.reasoning.confidence_engine import compute_confidence
from backend.reasoning.archetype_calibration import calibrate_archetype_weights
from backend.retrieval.evidence_router import route_evidence
import json


def is_real_momentum_signal(text: str) -> bool:
    """Accepts launches, shipping velocity, adoption, partnerships, hiring, and funding."""
    EVENT_TERMS = [
        # Launches / Releases
        "announce", "launch", "release", "introduc", "publish", "update", "new feature", "now available", "beta", "general availability",
        # Partnerships
        "partner", "collaboration", "integration with", 
        # Acquisitions / Funding
        "acquir", "acquisition", "funding", "invest", "raised", "series",
        # Hiring / Expansion
        "hiring", "expand", "expansion", "open roles", "careers",
        # Adoption / Velocity
        "engineers", "adoption", "users", "growing from", "% of", "thousands",
        "millions", "used by", "changelog", "improvement", "award", "breakthrough"
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

def sanitize_momentum_evidence(signals_dict: dict, diagnostics: bool = False):
    metrics = {
        "signals_extracted": 0,
        "signals_preserved": 0,
        "signals_dropped": 0,
        "rejected_reasons": []
    }
    
    if not signals_dict:
        return (signals_dict, metrics) if diagnostics else signals_dict
        
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
            metrics["signals_extracted"] += 1
            if any(pat in ev.lower() for pat in HISTORICAL_MOMENTUM_PATTERNS):
                metrics["signals_dropped"] += 1
                metrics["rejected_reasons"].append(f"historical: {ev[:30]}...")
                continue
            if is_marketing_copy(ev) and not is_real_momentum_signal(ev):
                metrics["signals_dropped"] += 1
                metrics["rejected_reasons"].append(f"marketing_noise: {ev[:30]}...")
                continue
            # Only validate real-event types for launch; always pass adoption/velocity
            if category in ("launch_signals",) and not is_real_momentum_signal(ev):
                metrics["signals_dropped"] += 1
                metrics["rejected_reasons"].append(f"not_real_launch: {ev[:30]}...")
                continue
            clean_list.append(ev)
            metrics["signals_preserved"] += 1
        if clean_list:
            sanitized[category] = clean_list
    return (sanitized, metrics) if diagnostics else sanitized

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

    metrics = {}
    if signals:
        sanitized_signals, metrics = sanitize_momentum_evidence(signals, diagnostics=True)

        # Build structured context
        momentum_context = "MOMENTUM SIGNALS\n\n"
        momentum_context += "Below are structured signals extracted from the source content.\n\n"

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

        # Separate raw chunks strongly to avoid context leakage
        if chunks:
            raw_sample = [c for c in chunks if len(c.strip()) > 50][:5]
            if raw_sample:
                momentum_context += "\n\n--- FALLBACK RAW CONTEXT ---\n"
                if total_evidence > 0:
                    momentum_context += "WARNING: You already have structured signals above. Rely on them first. Only use this raw context if absolutely necessary. Do NOT hallucinate signals.\n\n"
                else:
                    momentum_context += "WARNING: No structured signals available. You may carefully extract momentum signals from the raw context below, but do not hallucinate.\n\n"
                for i, chunk in enumerate(raw_sample, 1):
                    momentum_context += f"[{i}] {chunk[:600]}\n\n"
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
    # Strategy reasoning
    # -----------------------------------
    
    import json
    
    # We pass the extracted signals as context. Since signals is a dict, we can dump it.
    signals_context = json.dumps(signals, indent=2) if signals else "{}"
    
    strategy_result = await analyze_strategy(
        signals_context=signals_context,
        tone_output=tone_result,
        icp_output=icp_result
    )

    # -----------------------------------
    # Archetype reasoning
    # -----------------------------------
    
    archetype_result = await score_archetypes(
        tone_output=tone_result,
        icp_output=icp_result,
        strategy_output=strategy_result,
        momentum_output=momentum_result
    )
    
    import json
    archetype_result_str = json.dumps(archetype_result, indent=2)

    # -----------------------------------
    # Strategic synthesis
    # -----------------------------------
    
    full_context_str = "\n\n".join(chunks)

    final_result_str = await synthesize_intelligence(

        context=full_context_str,

        momentum_analysis=momentum_result,

        tone_analysis=tone_result,

        icp_analysis=icp_result,
        
        strategy_analysis=strategy_result,
        
        archetype_analysis=archetype_result_str,

        validation=validation
    )

    # -----------------------------------
    # Confidence & Calibration Post-Processing
    # -----------------------------------
    # Extract JSON between first { and last } (handles models that prepend text before the JSON)
    start_idx = final_result_str.find("{")
    end_idx = final_result_str.rfind("}")

    if start_idx != -1 and end_idx != -1:
        cleaned_json_str = final_result_str[start_idx:end_idx+1]
    else:
        cleaned_json_str = final_result_str

    try:
        final_data = json.loads(cleaned_json_str)
    except json.JSONDecodeError:
        # Fallback if synthesis failed to output json
        final_data = {}

    registry = EvidenceRegistry()
    
    # Extract evidence fields generated by LLM
    evidence_mappings = [
        ("core_offering", "core_offering_evidence", "core_offering_source", "core_offering_source_url"),
        ("pricing_signals", "pricing_evidence", "pricing_source", "pricing_source_url"),
        ("hiring_signals", "hiring_evidence", "hiring_source", "hiring_source_url"),
        ("strategic_keywords", "keywords_evidence", "keywords_source", "keywords_source_url"),
        ("icp", "icp_evidence", "icp_source", "icp_source_url"),
        ("messaging_tone", "tone_evidence", "tone_source", "tone_source_url"),
        ("recent_launches", "momentum_evidence", "momentum_source", "momentum_source_url"),
        ("growth_signals", "momentum_evidence", "momentum_source", "momentum_source_url"),
        ("risk_flags", "risk_evidence", "risk_source", "risk_source_url"),
        ("momentum_score", "momentum_evidence", "momentum_source", "momentum_source_url"),
        ("analyst_note", "analyst_evidence", "analyst_source", "analyst_source_url")
    ]
    
    for field_name, ev_key, src_key, url_key in evidence_mappings:
        ev_list = final_data.get(ev_key, [])
        if not isinstance(ev_list, list):
            ev_list = [ev_list] if isinstance(ev_list, str) else []
            
        src_val = final_data.get(src_key, "unknown")
        url_val = final_data.get(url_key, "")
        
        for ev_str in ev_list:
            if isinstance(ev_str, str) and ev_str:
                registry.add_evidence(field_name, ev_str, url_val, src_val, src_val)

    # Compute confidence for each field
    confidence_metrics = {}
    for field_name, ev_key, src_key, url_key in evidence_mappings:
        items = [e["evidence"] for e in registry.get_evidence(field_name)]
        sources = [e["source_type"] for e in registry.get_evidence(field_name)]
        conf_data = compute_confidence(field_name, items, sources)
        confidence_metrics[field_name] = conf_data

    # Save to top level to preserve frontend string flat schema
    final_data["confidence_metrics"] = confidence_metrics
    
    # Calibrate archetype
    calibrated_archetype = calibrate_archetype_weights(archetype_result, registry)

    # Always write competitor_dna unconditionally from calibrated archetype.
    # This guarantees the field is present even when the synthesis LLM omits it.
    existing_dna = final_data.get("competitor_dna") or {}
    winner = calibrated_archetype.get("winner", {})
    existing_dna["archetype"] = winner.get("archetype", existing_dna.get("archetype"))
    existing_dna["confidence"] = winner.get("confidence", existing_dna.get("confidence"))
    existing_dna["alternative_archetypes"] = calibrated_archetype.get("candidates", existing_dna.get("alternative_archetypes", []))
    existing_dna["supporting_signals"] = winner.get("supporting_signals", existing_dna.get("supporting_signals", []))
    final_data["competitor_dna"] = existing_dna

    final_result_str = json.dumps(final_data)

    return {

        "momentum": momentum_result,

        "tone": tone_result,

        "icp": icp_result,
        
        "strategy": strategy_result,
        
        "archetype": calibrated_archetype,

        "final": final_result_str,
        
        "preservation_metrics": metrics
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