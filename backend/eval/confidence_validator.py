from collections import Counter
from backend.models.schemas import CompetitorAnalysis

def score_confidence_calibration(analysis: CompetitorAnalysis) -> float:
    """
    Detects if confidence values are anchored to prompt examples or repeated lazily.
    Returns a score from 0.0 to 1.0.
    """
    scores = analysis.confidence_scores
    if not scores:
        return 1.0

    values = list(scores.values())
    
    penalty = 0.0
    
    # 1. Penalize exact matches to prompt defaults (92, 88, 85, 75)
    prompt_defaults = {92, 88, 85, 75}
    for val in values:
        if val in prompt_defaults:
            penalty += 0.2
            
    # 2. Penalize repeated values across different fields
    # If the model gives 85 to 4 different fields, it's not calibrated
    counts = Counter(values)
    for val, count in counts.items():
        if count > 1:
            penalty += 0.15 * (count - 1)
            
    final_score = max(0.0, 1.0 - penalty)
    return final_score
