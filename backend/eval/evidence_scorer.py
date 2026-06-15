from backend.models.schemas import CompetitorAnalysis

def score_evidence_quality(analysis: CompetitorAnalysis) -> float:
    """
    Measures the quality of evidence supporting the analysis.
    Higher score when conclusions are supported by multiple evidence fields and diverse sources.
    """
    evidence_fields = [
        "core_offering_evidence", "pricing_evidence", "hiring_evidence", 
        "keywords_evidence", "icp_evidence", "tone_evidence", "momentum_evidence"
    ]
    
    source_url_fields = [
        "core_offering_source_url", "pricing_source_url", "hiring_source_url", "keywords_source_url"
    ]
    
    score = 0.0
    
    # 1. Evidence count / section coverage
    evidence_populated = 0
    for field in evidence_fields:
        val = getattr(analysis, field, [])
        if val and isinstance(val, list) and len(val) > 0:
            evidence_populated += 1
            
    # Max evidence score component is 0.7
    if evidence_populated >= 4:
        score += 0.7
    elif evidence_populated > 0:
        score += (evidence_populated / 4.0) * 0.7
        
    # 2. Source diversity
    unique_sources = set()
    for field in source_url_fields:
        val = getattr(analysis, field, None)
        if val and isinstance(val, str) and val.strip():
            unique_sources.add(val.strip())
            
    if len(unique_sources) >= 2:
        score += 0.3
    elif len(unique_sources) == 1:
        score += 0.15
        
    return min(1.0, score)
