from backend.reasoning.archetype_calibration import calibrate_archetype_weights
from backend.reasoning.evidence_registry import EvidenceRegistry

def test_archetype_calibration_anthropic():
    registry = EvidenceRegistry()
    registry.add_evidence("core_offering", "We focus on governance, compliance, and security for regulated industries")
    
    initial_results = {
        "winner": {"archetype": "AI Platform Builder", "confidence": 0.42},
        "candidates": [
            {"archetype": "Trusted Enterprise AI", "confidence": 0.13}
        ]
    }
    
    calibrated = calibrate_archetype_weights(initial_results, registry)
    
    # Because 'governance', 'compliance', 'security', 'regulated' are present, Trusted Enterprise AI should get a massive boost
    # and overtake AI Platform Builder
    assert calibrated["winner"]["archetype"] == "Trusted Enterprise AI"
    assert calibrated["winner"]["confidence"] > 0.42
