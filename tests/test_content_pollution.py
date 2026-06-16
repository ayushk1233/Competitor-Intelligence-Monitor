import pytest
from backend.intelligence.content_quality import clean_content

def test_content_pollution_removal():
    raw_text = """
    Plan a surf trip to Costa Rica
    Find hiking boots for wide feet
    Fantasy football team names
    Teach me Mahjong
    Help me debug this code
    What can I help with?
    Try ChatGPT
    OpenAI has launched GPT-5, an open-source model.
    Download on the App Store
    Get it on Google Play
    Skip to content
    Menu
    Search
    We are hiring engineers for our new OpenAI Academy.
    Copyright 2026 OpenAI. All rights reserved.
    """
    
    cleaned_text, metrics = clean_content(raw_text)
    
    # Assertions for noise removal
    assert "Plan a surf trip" not in cleaned_text
    assert "Find hiking boots" not in cleaned_text
    assert "Fantasy football" not in cleaned_text
    assert "Teach me Mahjong" not in cleaned_text
    assert "Help me debug this code" not in cleaned_text
    assert "What can I help with" not in cleaned_text
    assert "Try ChatGPT" not in cleaned_text
    assert "Download on the App Store" not in cleaned_text
    assert "Copyright 2026" not in cleaned_text
    
    # Assertions for signal preservation
    assert "GPT-5" in cleaned_text
    assert "OpenAI Academy" in cleaned_text
    
    # Assertions for metrics
    assert metrics["noise_removed_count"] > 0
    assert metrics["content_retention_ratio"] < 100.0
    assert len(metrics["noise_removed_examples"]) > 0
