import pytest
from backend.reasoning.orchestrator import sanitize_momentum_evidence

def test_signal_preservation_diagnostics():
    signals = {
        "launch_signals": [
            "We launched a new product today.",
            "This is just some generic next-generation ai noise.",
            "Founded 23 years ago in a garage."
        ]
    }
    
    sanitized, metrics = sanitize_momentum_evidence(signals, diagnostics=True)
    
    assert metrics["signals_extracted"] == 3
    assert metrics["signals_preserved"] == 1
    assert metrics["signals_dropped"] == 2
    
    # Check drop reasons
    reasons = " ".join(metrics["rejected_reasons"])
    assert "marketing_noise" in reasons
    assert "historical" in reasons
    
    # Verify the actual output is correct
    assert "We launched a new product today." in sanitized["launch_signals"]
    assert "next-generation ai" not in " ".join(sanitized["launch_signals"])

def test_signal_preservation_no_diagnostics():
    signals = {
        "launch_signals": ["We launched a new product today."]
    }
    
    # Should not return tuple
    result = sanitize_momentum_evidence(signals, diagnostics=False)
    assert isinstance(result, dict)
    assert "launch_signals" in result
