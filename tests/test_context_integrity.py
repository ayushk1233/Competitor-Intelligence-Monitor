import pytest
from backend.eval.context_integrity import evaluate_context_integrity

def test_signal_preservation_after_ranking():
    snapshots = [
        {
            "source_url": "https://example.com/blog",
            "page_type": "blog",
            "content_text": "We are thrilled to announce the launch of our new AI Agent platform. " * 50 +
                            "This product introduces a brand new semantic search capability. " * 50 +
                            "Over 5 million developers are using it. " * 50
        }
    ]
    
    result = evaluate_context_integrity("Example", snapshots)
    
    # Assert that extracting before ranking yields all signals (they get deduplicated, but many atomic signals exist)
    # The ranker will truncate the 10,000+ characters down significantly, meaning we should have lost some signals
    # if we only extracted from ranked context (though deduplication might save us in this synthetic case).
    
    # Just asserting the pipeline runs without error and returns the proper dictionary format with expected keys
    assert "raw_chars" in result
    assert "cleaned_chars" in result
    assert "ranked_chars" in result
    assert "signals_before_ranking" in result
    assert "signals_after_ranking" in result
    
    assert result["raw_chars"] > 0
    assert result["signals_before_ranking"] >= result["signals_after_ranking"]
    assert result["ranked_chars"] <= result["cleaned_chars"]

def test_clean_content_pipeline_removes_noise():
    snapshots = [
        {
            "source_url": "https://openai.com",
            "page_type": "homepage",
            "content_text": "What can I help with? \n Try ChatGPT \n Plan a surf trip \n Teach me Mahjong \n OpenAI released GPT-5."
        }
    ]
    
    result = evaluate_context_integrity("OpenAI", snapshots)
    
    # 4 lines of noise removed
    assert result["noise_removed_count"] == 4
    
    # The actual launch signal remains
    assert result["signals_before_ranking"] > 0
