import re
import json
from backend.reasoning.archetype_registry import ARCHETYPE_REGISTRY
from backend.services.llm_service import call_openrouter

HYPOTHESIS_PROMPT = """
You are a strategic intelligence analyst.
Given the company's winning archetype and the specific supporting signals extracted from their recent activity, generate hypotheses about their LIKELY NEXT MOVES and EXPANSION VECTOR.

Return ONLY valid JSON.

Schema:
{
  "expansion_vector": "One sentence describing where they are expanding next",
  "likely_next_moves": [
    {
      "hypothesis": "Specific hypothesized move based on the signals",
      "confidence": "high|medium|low"
    }
  ]
}

Focus on structured hypothesis generation. Do NOT invent new signals.
"""

async def generate_hypotheses(archetype: str, supporting_signals: list) -> dict:
    if not supporting_signals:
        return {
            "expansion_vector": "Unknown based on current signals",
            "likely_next_moves": []
        }
        
    user_prompt = f"""
ARCHETYPE: {archetype}

SUPPORTING SIGNALS DETECTED:
{chr(10).join(f"- {s}" for s in supporting_signals)}

Generate the expansion vector and likely next moves hypotheses.
"""
    response = await call_openrouter(
        prompt=user_prompt,
        system_prompt=HYPOTHESIS_PROMPT,
        call_type="hypothesis"
    )
    if not response:
        return {}
        
    response = response.strip()
    response = response.replace("```json", "").replace("```", "")
    try:
        return json.loads(response.strip())
    except Exception:
        return {}


async def score_archetypes(
    tone_output: str,
    icp_output: str,
    strategy_output: str,
    momentum_output: str
):
    # 1. Combine all text for scoring
    combined_text = f"{tone_output} {icp_output} {strategy_output} {momentum_output}".lower()
    
    # 2. Score archetypes
    scores = {}
    supporting_signals_map = {}
    
    for archetype, data in ARCHETYPE_REGISTRY.items():
        score = 0
        signals_found = []
        
        for keyword, weight in data["positive_signals"].items():
            # Use regex for word boundary matching to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined_text):
                score += weight
                signals_found.append(keyword)
                
        scores[archetype] = score
        supporting_signals_map[archetype] = signals_found
        
    # 3. Normalize scores
    total_score = sum(scores.values())
    
    normalized = {}
    for arch, score in scores.items():
        if total_score > 0:
            normalized[arch] = round(score / total_score, 2)
        else:
            normalized[arch] = 0.0
            
    # 4. Sort archetypes by score descending, then by number of unique signals matched
    sorted_archetypes_raw = sorted(scores.items(), key=lambda x: (x[1], len(supporting_signals_map[x[0]])), reverse=True)
    
    # Map back to normalized confidence for the output
    sorted_archetypes = [(arch, normalized[arch]) for arch, _ in sorted_archetypes_raw]
    # If no keywords matched at all, just return empty/unknown
    if total_score == 0:
        return {
            "winner": {
                "archetype": "Unknown",
                "confidence": 0.0,
                "growth_model": "Unknown",
                "primary_moat": "Unknown",
                "strategic_risk": "Unknown",
                "supporting_signals": []
            },
            "candidates": [],
            "hypotheses": {}
        }
    
    winner_name, winner_conf = sorted_archetypes[0]
    winner_data = ARCHETYPE_REGISTRY[winner_name]
    
    winner = {
        "archetype": winner_name,
        "confidence": winner_conf,
        "growth_model": winner_data["growth_model"],
        "primary_moat": winner_data["primary_moat"],
        "strategic_risk": winner_data["strategic_risk"],
        "supporting_signals": supporting_signals_map[winner_name]
    }
    
    candidates = []
    for arch_name, conf in sorted_archetypes[1:4]: # Top 3 alternatives
        if conf > 0:
            candidates.append({
                "archetype": arch_name,
                "confidence": conf
            })
            
    # 5. Generate hypotheses for the winner based on its supporting signals
    hypotheses = await generate_hypotheses(winner_name, winner["supporting_signals"])
    
    return {
        "winner": winner,
        "candidates": candidates,
        "hypotheses": hypotheses
    }
