from backend.signals.enums import SignalSeverity
from backend.temporal.enums import TemporalChangeCategory

def calculate_severity(confidence_score: float) -> SignalSeverity:
    """
    Deterministic rule to map a continuous confidence score into a discrete severity band.
    """
    if confidence_score >= 0.90:
        return SignalSeverity.CRITICAL
    elif confidence_score >= 0.75:
        return SignalSeverity.HIGH
    elif confidence_score >= 0.50:
        return SignalSeverity.MEDIUM
    else:
        return SignalSeverity.LOW

def normalize_category(category_str: str) -> TemporalChangeCategory:
    """
    Deterministic rule to map arbitrary LLM category outputs into the rigorous Enum.
    (Though the parser already enforces this, this acts as an extra safety net or normalization 
    layer before extraction if the enum allows some variation).
    """
    # Currently TemporalChangeCategory is strict. We just cast it for safety.
    try:
        return TemporalChangeCategory(category_str.lower())
    except ValueError:
        return TemporalChangeCategory.UNKNOWN
