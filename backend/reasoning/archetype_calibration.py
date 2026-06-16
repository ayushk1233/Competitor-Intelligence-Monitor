from backend.reasoning.evidence_registry import EvidenceRegistry

def calibrate_archetype_weights(archetype_results: dict, registry: EvidenceRegistry) -> dict:
    """
    Adjusts archetype scores and candidate confidences based on specific evidence found
    in the pipeline. For example, 'Trusted Enterprise AI' should score higher if 
    governance/compliance evidence is present.
    """
    # Calibration registry
    CALIBRATION_RULES = [
        {
            "keyword": "governance",
            "weight": 15,
            "archetype": "Trusted Enterprise AI"
        },
        {
            "keyword": "compliance",
            "weight": 15,
            "archetype": "Trusted Enterprise AI"
        },
        {
            "keyword": "regulated",
            "weight": 10,
            "archetype": "Trusted Enterprise AI"
        },
        {
            "keyword": "security",
            "weight": 10,
            "archetype": "Trusted Enterprise AI"
        },
        {
            "keyword": "audit",
            "weight": 10,
            "archetype": "Trusted Enterprise AI"
        },
        {
            "keyword": "trust",
            "weight": 10,
            "archetype": "Trusted Enterprise AI"
        },
        # AI Platform / Developer ecosystem
        {
            "keyword": "developer",
            "weight": 3,
            "archetype": "AI Platform Builder"
        },
        {
            "keyword": "ecosystem",
            "weight": 3,
            "archetype": "AI Platform Builder"
        },
        # Distribution
        {
            "keyword": "distribution",
            "weight": 10,
            "archetype": "AI Distribution Platform"
        }
    ]
    
    # Extract all evidence text across all fields
    all_evidence = []
    for entry in registry.evidence:
        all_evidence.append(entry["evidence"].lower())
        
    all_text = " ".join(all_evidence)
    
    # Compute boosts
    boosts = {}
    for rule in CALIBRATION_RULES:
        if rule["keyword"] in all_text:
            arch = rule["archetype"]
            boosts[arch] = boosts.get(arch, 0) + rule["weight"]
            
    if not boosts:
        return archetype_results
        
    # We will adjust the confidences of the winner and the alternatives based on the boosts.
    # We treat existing confidence like "base points" out of 100.
    
    candidates = {}
    
    winner = archetype_results.get("winner", {})
    if winner:
        arch_name = winner.get("archetype")
        candidates[arch_name] = {"confidence": winner.get("confidence", 0.0), "is_winner": True, "obj": winner}
        
    for alt in archetype_results.get("candidates", []):
        arch_name = alt.get("archetype")
        candidates[arch_name] = {"confidence": alt.get("confidence", 0.0), "is_winner": False, "obj": alt}
        
    # Apply boosts
    for arch_name, boost in boosts.items():
        if arch_name in candidates:
            # increase confidence (treating 0.01 as 1 point)
            candidates[arch_name]["confidence"] += (boost / 100.0)
        else:
            # It wasn't even a candidate, add it with low confidence based on boost
            candidates[arch_name] = {
                "confidence": (boost / 100.0),
                "is_winner": False,
                "obj": {
                    "archetype": arch_name,
                    "confidence": 0.0
                }
            }
            
    # Re-normalize
    total_conf = sum(c["confidence"] for c in candidates.values())
    if total_conf > 0:
        for arch_name in candidates:
            candidates[arch_name]["confidence"] = round(candidates[arch_name]["confidence"] / total_conf, 2)
            
    # Sort to find new winner
    sorted_candidates = sorted(candidates.values(), key=lambda x: x["confidence"], reverse=True)
    
    if not sorted_candidates:
        return archetype_results
        
    # Build new result
    new_winner_data = sorted_candidates[0]
    new_winner_obj = dict(new_winner_data["obj"])
    new_winner_obj["confidence"] = new_winner_data["confidence"]
    # If the winner swapped, we might miss some supporting signals, but we'll leave them as is for now.
    
    new_candidates_list = []
    for c in sorted_candidates[1:]:
        alt_obj = dict(c["obj"])
        alt_obj["confidence"] = c["confidence"]
        new_candidates_list.append(alt_obj)
        
    return {
        "winner": new_winner_obj,
        "candidates": new_candidates_list,
        "hypotheses": archetype_results.get("hypotheses", [])
    }
