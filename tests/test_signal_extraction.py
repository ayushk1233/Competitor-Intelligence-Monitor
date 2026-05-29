from backend.retrieval.signal_extractor import extract_signals

def test_extract_signals_ai_and_launch():
    sample = "OpenAI partnership announced. They are building a reasoning model."
    signals = extract_signals(sample)
    
    assert "launch_signals" in signals
    assert "ai_initiatives" in signals
    assert len(signals["launch_signals"]) > 0
    assert len(signals["ai_initiatives"]) > 0

def test_extract_signals_hiring_and_enterprise():
    sample = "We are recruiting for enterprise-grade deployment experts."
    signals = extract_signals(sample)
    
    assert "hiring_signals" in signals
    assert "enterprise_signals" in signals
    assert "technical_signals" in signals # 'deployment' is in technical

def test_extract_signals_does_not_match_random():
    sample = "This is just a normal company selling shoes."
    signals = extract_signals(sample)
    assert not signals
