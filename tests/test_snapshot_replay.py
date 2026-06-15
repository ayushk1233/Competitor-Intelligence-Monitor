import pytest
import json
import os
from backend.eval.replay_runner import run_replay_for_company

@pytest.fixture
def snapshots_data():
    path = "tests/mock_snapshots.json"
    if not os.path.exists(path):
        pytest.skip("Mock snapshots not found")
    with open(path, "r") as f:
        return json.load(f)

def test_openai_replay(snapshots_data):
    result = run_replay_for_company("Openai", snapshots_data)
    assert result.signals_preserved / result.signals_extracted > 0.8
    assert result.momentum_score > 1
    
    # Check for GPT-5 or Academy
    launches = "\n".join(result.launch_signals).lower()
    assert "gpt-5" in launches or "academy" in launches or "chatgpt" in launches
    
    # Check partnerships
    assert len(result.partnership_signals) > 0

def test_anthropic_replay(snapshots_data):
    result = run_replay_for_company("Anthropic", snapshots_data)
    assert result.momentum_score > 1
    
    # Check hiring signals preserved
    assert len(result.hiring_signals) > 0

def test_google_replay(snapshots_data):
    result = run_replay_for_company("Google", snapshots_data)
    assert result.momentum_score > 1
    
    # Check Gemini or Cloud preserved
    launches = "\n".join(result.launch_signals).lower()
    assert "gemini" in launches or "cloud" in launches
