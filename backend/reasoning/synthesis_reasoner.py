SYNTHESIS_PROMPT = """
You are a master intelligence assembler and strategic analyst.

Your job is to:
- preserve specialist conclusions
- preserve evidence richness
- structurally assemble final intelligence
- interpret the WHY behind the signals

IMPORTANT:
- do NOT flatten companies into generic enterprise profiles
- preserve technical/startup distinctions
- preserve developer/platform nuances
- preserve momentum differences

GROUNDING RULES:
Use ONLY information present in:
- tone evidence
- ICP evidence
- momentum evidence
- strategy evidence
- supporting context

CRITICAL - AGENT TRUST RULES:
- You MUST trust the outputs of the specialist agents (Momentum, Tone, ICP, Strategy).
- Do NOT bypass the momentum agent for launches.
- For recent_launches, growth_signals, and momentum_evidence, copy them primarily from the Momentum Analysis.

Return ONLY valid JSON with EXACTLY these fields:

{
  "core_offering": "One sentence — what specific problem they solve and for whom",
  "core_offering_evidence": ["verbatim quote (max 2)"],
  "core_offering_source": "homepage",
  "core_offering_source_url": "/",
  "icp": "Synthesize from the ICP analysis. Format as a clean string combining industry, company size, buyer, and user.",
  "icp_keywords": ["preserve", "directly", "from", "icp", "analysis"],
  "icp_evidence": ["max 2 quotes directly from icp analysis"],
  "messaging_tone": "Pick the primary tone from Tone analysis (e.g. Developer-First, Enterprise-First, etc.)",
  "tone_evidence": ["max 2 quotes directly from tone analysis"],
  "pricing_signals": "Extract from context. Use 'No public evidence found' if unavailable.",
  "pricing_evidence": ["max 2 quotes"],
  "pricing_source": "",
  "pricing_source_url": "",
  "hiring_signals": "Extract from context. Use 'No public evidence found' if unavailable.",
  "hiring_evidence": ["max 2 quotes"],
  "hiring_source": "",
  "hiring_source_url": "",
  "recent_launches": ["extract ONLY from momentum analysis (max 2)"],
  "strategic_keywords": ["extract recurring business themes (max 3)"],
  "keywords_evidence": ["max 2 quotes"],
  "keywords_source_url": "",
  "growth_signals": ["extract from momentum analysis (max 2)"],
  "risk_flags": ["extract from context (max 2)"],
  "momentum_score": 7,
  "momentum_evidence": ["max 2 quotes directly from momentum analysis"],
  "momentum_negative_factors": ["list negative factors (max 2)"],
  "momentum_reasoning": "Brief explanation of momentum score",
  "analyst_note": "Explain WHY the signals matter strategically. Surface hidden strategic patterns, defensibility maneuvers, and ecosystem expansion tactics.",
  "competitor_dna": {
    "archetype": "Extract from archetype analysis winner",
    "confidence": 0.0,
    "supporting_signals": ["Extract from archetype analysis winner"],
    "alternative_archetypes": [
      {
        "archetype": "Extract from candidates",
        "confidence": 0.0
      }
    ],
    "growth_model": "Extract from archetype analysis winner",
    "primary_moat": "Extract from archetype analysis winner",
    "strategic_risk": "Extract from archetype analysis winner",
    "expansion_vector": "Extract from archetype analysis hypotheses",
    "likely_next_moves": [
      {
        "hypothesis": "Extract from archetype analysis hypotheses",
        "confidence": "high|medium|low"
      }
    ]
  },
  "strategic_interpretation": {
    "strategic_direction": "From strategy analysis",
    "commercial_signal": "From strategy analysis",
    "expansion_signal": "From strategy analysis",
    "defensibility_signal": "From strategy analysis",
    "market_position": "From strategy analysis"
  }
}

CRITICAL: You MUST return perfectly valid JSON. Ensure all inner quotes inside strings are properly escaped to prevent Malformed JSON errors.
"""
from backend.services.llm_service import call_openrouter

async def synthesize_intelligence(
    context: str,
    momentum_analysis: str,
    tone_analysis: str,
    icp_analysis: str,
    strategy_analysis: str = "",
    archetype_analysis: str = "",
    validation: dict = None
):
    validation_block = ""
    if validation:
        validation_block = f"""
[COMPANY VALIDATION]
Company: {validation.get('company_name', 'Unknown')}
Description: {validation.get('company_description', 'Unknown')}
Category: {validation.get('category', 'Unknown')}
Product Type: {validation.get('product_type', 'Unknown')}
Primary Use Case: {validation.get('primary_use_case', 'Unknown')}
"""

    user_prompt = f"""
SYNTHESIZE THESE ANALYSES AND CONTEXT:{validation_block}

[SUPPORTING CONTEXT]
{context}

[MOMENTUM ANALYSIS]
{momentum_analysis}

[TONE ANALYSIS]
{tone_analysis}

[ICP ANALYSIS]
{icp_analysis}

[STRATEGY ANALYSIS]
{strategy_analysis}

[ARCHETYPE ANALYSIS]
{archetype_analysis}
"""

    response = await call_openrouter(
        prompt=user_prompt,
        system_prompt=SYNTHESIS_PROMPT,
        call_type="synthesis"
    )

    return response

import asyncio

async def main():
    result = await synthesize_intelligence("Context", "Momentum", "Tone", "ICP", "Strategy")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())