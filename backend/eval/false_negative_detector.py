from backend.models.schemas import CompetitorAnalysis

def score_false_negatives(analysis: CompetitorAnalysis) -> float:
    """
    Detects if there are false negative conclusions when actual evidence exists.
    e.g., Output claims 'No hiring detected' but hiring_evidence array is populated.
    """
    penalty = 0.0
    
    negative_phrases = [
        "no public evidence found",
        "not detected",
        "insufficient information available",
        "no hiring detected",
        "none",
        "n/a"
    ]
    
    # 1. Growth Signals vs Launches
    if analysis.recent_launches and len(analysis.recent_launches) > 0:
        growth_text = " ".join(analysis.growth_signals).lower() if isinstance(analysis.growth_signals, list) else str(analysis.growth_signals).lower()
        if any(p in growth_text for p in negative_phrases):
            penalty += 0.3
            
    # 2. Hiring Signals vs Evidence
    hiring_evidence = getattr(analysis, "hiring_evidence", [])
    if hiring_evidence and len(hiring_evidence) > 0:
        if any(p in str(analysis.hiring_signals).lower() for p in negative_phrases):
            penalty += 0.3
            
    # 3. Pricing Signals vs Evidence
    pricing_evidence = getattr(analysis, "pricing_evidence", [])
    if pricing_evidence and len(pricing_evidence) > 0:
        if any(p in str(analysis.pricing_signals).lower() for p in negative_phrases):
            penalty += 0.3

    final_score = max(0.0, 1.0 - penalty)
    return final_score
