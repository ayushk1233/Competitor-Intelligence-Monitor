from backend.reasoning.agreement_score import compute_agreement_score

def compute_confidence(field_name: str, evidence_items: list[str], source_metadata: list[str]) -> dict:
    evidence_count = len(evidence_items)
    unique_sources = list(set(source_metadata)) if source_metadata else []
    source_count = len(unique_sources)
    
    # Base configuration per field type
    # For some fields, 1 piece of evidence is enough to be fairly confident (e.g. pricing)
    # For others like messaging_tone, we want more evidence.
    expected_evidence = 3
    expected_sources = 2
    
    if field_name in ["pricing_signals", "core_offering", "momentum_score", "recent_launches"]:
        expected_evidence = 2
        expected_sources = 1
    elif field_name in ["strategic_keywords", "risk_flags", "growth_signals"]:
        expected_evidence = 4
        expected_sources = 2

    # Calculate sub-scores
    # 1. Evidence Score (max 0.4)
    evidence_ratio = min(1.0, evidence_count / expected_evidence) if expected_evidence > 0 else 1.0
    evidence_score = 0.4 * evidence_ratio
    
    # 2. Source Diversity Score (max 0.3)
    source_ratio = min(1.0, source_count / expected_sources) if expected_sources > 0 else 1.0
    source_score = 0.3 * source_ratio
    
    # 3. Agreement Score (max 0.3)
    agreement = compute_agreement_score(evidence_items)
    agreement_score_contribution = 0.3 * agreement
    
    # Total confidence
    if evidence_count == 0:
        total_confidence = 0.0
    else:
        total_confidence = evidence_score + source_score + agreement_score_contribution
        
    return {
        "confidence": round(total_confidence, 2),
        "evidence_count": evidence_count,
        "source_count": source_count,
        "source_types": unique_sources,
        "agreement_score": round(agreement, 2)
    }
