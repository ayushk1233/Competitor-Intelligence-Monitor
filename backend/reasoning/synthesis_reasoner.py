SYNTHESIS_PROMPT = """
You are a senior competitive intelligence strategist.

Your job is to synthesize multiple specialized analyses into a final strategic intelligence profile, and extract any remaining strategic signals from the raw context.

You will receive:
- momentum analysis
- tone analysis
- ICP analysis
- original supporting context

Produce a unified strategic assessment.

Return ONLY valid JSON with exactly these fields:

{
  "core_offering": "One sentence — what specific problem they solve and for whom",
  "icp": "Synthesize from the ICP analysis",
  "messaging_tone": "Pick exactly one: enterprise | startup | technical | visionary | hybrid (from Tone analysis)",
  "pricing_signals": "Extract from context. Write Not detected if unavailable.",
  "hiring_signals": "Extract from context. Write Not detected if unavailable.",
  "recent_launches": ["extract", "from", "context", "or", "momentum", "analysis"],
  "strategic_keywords": ["extract", "from", "context"],
  "growth_signals": ["extract", "from", "context", "or", "momentum", "analysis"],
  "risk_flags": ["extract", "from", "context"],
  "momentum_score": 7,
  "analyst_note": "One hard-hitting strategic observation summarizing the synthesis"
}

Keep reasoning concise and strategic.
"""
from backend.services.llm_service import (
    call_openrouter
)


async def synthesize_intelligence(

    context: str,

    momentum_analysis: str,

    tone_analysis: str,

    icp_analysis: str
):

    user_prompt = f"""
SYNTHESIZE THESE ANALYSES AND CONTEXT:

[SUPPORTING CONTEXT]
{context}

[MOMENTUM ANALYSIS]
{momentum_analysis}

[TONE ANALYSIS]
{tone_analysis}

[ICP ANALYSIS]
{icp_analysis}
"""

    response = await call_openrouter(

        prompt=user_prompt,

        system_prompt=SYNTHESIS_PROMPT
    )

    return response

import asyncio


async def main():

    momentum = """
    Momentum score: 8
    Strong AI launches and hiring.
    """

    tone = """
    Tone: enterprise technical.
    Strong developer positioning.
    """

    icp = """
    ICP: enterprise engineering teams.
    """

    result = await synthesize_intelligence(

        "Sample context string",

        momentum,

        tone,

        icp
    )

    print(result)


if __name__ == "__main__":

    asyncio.run(main())