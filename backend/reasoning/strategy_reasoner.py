STRATEGY_PROMPT = """
You are an elite competitive intelligence strategist.

Your goal is to convert isolated signals (launches, partnerships, hiring, pricing) into STRATEGIC MEANING.
Explain what the company's maneuvers indicate about their broader market positioning, defensibility, and ecosystem strategy.

Input will include:
- Extracted Signals (Launches, Partnerships, etc.)
- Tone Classification
- ICP Breakdown

Return ONLY valid JSON.

Schema:
{
  "strategic_direction": "",
  "commercial_signal": "",
  "expansion_signal": "",
  "defensibility_signal": "",
  "market_position": ""
}

Focus on:
- strategic_direction: What is their overarching goal? (e.g., "Ecosystem lock-in via developer platform")
- commercial_signal: What do their moves say about revenue generation?
- expansion_signal: Where are they moving next?
- defensibility_signal: How are they building a moat?
- market_position: How do they differentiate from competitors?

Return JSON ONLY.
"""

from backend.services.llm_service import call_openrouter
import json

async def analyze_strategy(
    signals_context: str,
    tone_output: str,
    icp_output: str
):
    user_prompt = f"""
Analyze the company's strategic direction based on the following intelligence:

SIGNALS:
{signals_context}

TONE ANALYSIS:
{tone_output}

ICP ANALYSIS:
{icp_output}
"""
    response = await call_openrouter(
        prompt=user_prompt,
        system_prompt=STRATEGY_PROMPT,
        call_type="strategy"
    )
    if not response:
        return "{}"
        
    response = response.strip()
    response = response.replace("```json", "").replace("```", "")
    return response.strip()
