class TemporalAnalysisError(Exception):
    """Raised when temporal analysis fails."""
    pass

class TimelineComparisonError(Exception):
    """Raised when timeline comparison encounters an issue (e.g. missing events)."""
    pass

class TemporalReasoningError(Exception):
    """Raised when the temporal reasoning engine fails to extract meaningful insights."""
    pass
