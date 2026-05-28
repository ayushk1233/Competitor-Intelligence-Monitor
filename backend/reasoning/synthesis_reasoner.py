SYNTHESIS_PROMPT = """
You are a senior competitive intelligence strategist.

Your job is to synthesize multiple specialized analyses into a final strategic intelligence profile.

You will receive:
- momentum analysis
- tone analysis
- ICP analysis

Produce a unified strategic assessment.

Return ONLY valid JSON with:

{
  "core_offering": "...",
  "icp": "...",
  "tone": "...",
  "momentum_score": 0,
  "strategic_summary": "...",
  "risk_flags": []
}

Keep reasoning concise and strategic.
"""
from backend.services.llm_service import (
    call_openrouter
)


async def synthesize_intelligence(

    momentum_analysis: str,

    tone_analysis: str,

    icp_analysis: str
):

    user_prompt = f"""
SYNTHESIZE THESE ANALYSES:

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

        momentum,

        tone,

        icp
    )

    print(result)


if __name__ == "__main__":

    asyncio.run(main())