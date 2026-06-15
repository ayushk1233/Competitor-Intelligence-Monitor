import pytest
from backend.eval.corruption_detector import detect_corruption

def test_detect_corruption_drop():
    trace = {
        "stage_3_compressed_signals": {
            "after_compression": {
                "launch_signals": ["New Feature A"]
            }
        },
        "stage_5_analyze_momentum": {
            "launch_signals_used": []
        },
        "stage_6_final_analysis": {
            "final_competitor_analysis": {
                "recent_launches": []
            }
        }
    }
    
    report = detect_corruption(trace)
    assert len(report["drops"]) == 1
    assert report["drops"][0]["signal"] == "New Feature A"
    assert len(report["mutations"]) == 0
    assert len(report["synthesis_hallucinations"]) == 0

def test_detect_corruption_mutation():
    trace = {
        "stage_3_compressed_signals": {
            "after_compression": {
                "launch_signals": ["New Feature A"]
            }
        },
        "stage_5_analyze_momentum": {
            "launch_signals_used": ["Completely different feature", "New Feature A"]
        },
        "stage_6_final_analysis": {
            "final_competitor_analysis": {
                "recent_launches": []
            }
        }
    }
    
    report = detect_corruption(trace)
    assert len(report["drops"]) == 0
    assert len(report["mutations"]) == 1
    assert report["mutations"][0]["signal"] == "Completely different feature"

def test_detect_synthesis_hallucination():
    trace = {
        "stage_3_compressed_signals": {
            "after_compression": {
                "launch_signals": ["New Feature A"]
            }
        },
        "stage_5_analyze_momentum": {
            "launch_signals_used": ["New Feature A"]
        },
        "stage_6_final_analysis": {
            "final_competitor_analysis": {
                "recent_launches": ["Hallucinated Feature B", "New Feature A"]
            }
        }
    }
    
    report = detect_corruption(trace)
    assert len(report["synthesis_hallucinations"]) == 1
    assert report["synthesis_hallucinations"][0]["signal"] == "Hallucinated Feature B"
