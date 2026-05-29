import pytest
from backend.retrieval.signal_extractor import extract_signals
from backend.reasoning.orchestrator import sanitize_momentum_evidence

def test_historical_launch_rejected():
    # Input: about a year after we first released it
    # Expected: launch_signals == []
    text = "about a year after we first released it"
    signals = extract_signals(text)
    assert "launch_signals" not in signals or len(signals["launch_signals"]) == 0

def test_historical_momentum_rejected():
    # Input: 27 years in business
    # Expected: momentum_signals == []
    signals = {
        "launch_signals": ["We have been 27 years in business and released many things."]
    }
    sanitized = sanitize_momentum_evidence(signals)
    assert "launch_signals" not in sanitized or len(sanitized["launch_signals"]) == 0

def test_historical_shipping_velocity_rejected():
    # Input: thousands of improvements over the years
    # Expected: shipping_velocity == [] (sanitized out)
    signals = {
        "shipping_velocity": ["thousands of improvements over the years"]
    }
    sanitized = sanitize_momentum_evidence(signals)
    assert "shipping_velocity" not in sanitized or len(sanitized["shipping_velocity"]) == 0

def test_founder_story_hiring_rejected():
    # Input: The founders stopped doing web design
    # Expected: hiring_signals == [] (sanitized out, or not extracted)
    text = "The founders stopped doing web design"
    signals = extract_signals(text)
    assert "hiring_signals" not in signals or len(signals["hiring_signals"]) == 0

def test_positive_recent_launch():
    # Input: Today we announced Basecamp 5 for 2026.
    # Expected: launch_signals contains the string
    text = "Today we announced Basecamp 5 for 2026."
    signals = extract_signals(text)
    assert "launch_signals" in signals
    assert len(signals["launch_signals"]) == 1
    assert "Today we announced Basecamp 5 for 2026." in signals["launch_signals"][0]
