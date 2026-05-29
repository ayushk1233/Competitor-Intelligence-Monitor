SYNTHESIS_PROMPT = """
You are an intelligence assembler.

Your job is NOT to reinterpret analyses.

Your job is to:
- preserve specialist conclusions
- preserve evidence richness
- structurally assemble final intelligence

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
- supporting context

Do not invent:
- partnerships
- funding
- growth percentages
- office expansions
- hiring numbers

If evidence is absent, return "Not detected".

Use specialist outputs heavily.

EXAMPLES:

Basecamp
tone=startup
momentum=2

Stripe
tone=technical
momentum=8

IBM
tone=enterprise
momentum=5

Return ONLY valid JSON with exactly these fields:

{
  "core_offering": "One sentence — what specific problem they solve and for whom",
  "icp": "Synthesize from the ICP analysis",
  "icp_keywords": ["preserve", "directly", "from", "icp", "analysis"],
  "icp_evidence": ["preserve", "directly", "from", "icp", "analysis"],
  "messaging_tone": "Pick exactly one: enterprise | startup | technical | visionary | hybrid (from Tone analysis)",
  "tone_evidence": ["preserve", "directly", "from", "tone", "analysis"],
  "pricing_signals": "Extract from context. Write Not detected if unavailable.",
  "hiring_signals": "Extract from context. Write Not detected if unavailable.",
  "recent_launches": ["extract", "from", "context", "or", "momentum", "analysis"],
  "strategic_keywords": ["extract", "from", "context. Extract recurring business themes. Examples: enterprise, payments, AI, automation, developer platform, CRM, compliance, workflow. Only include terms that appear multiple times or represent strategic focus. Avoid generic words."],
  "growth_signals": ["extract", "from", "context", "or", "momentum", "analysis"],
  "risk_flags": ["extract", "from", "context"],
  "momentum_score": 7,
  "momentum_evidence": ["preserve", "directly", "from", "momentum", "analysis"],
  "analyst_note": "One hard-hitting strategic observation summarizing the synthesis"
}

Do NOT invent new interpretations.
Do NOT override specialist agents.
Assemble conservatively.
CRITICAL: You MUST return perfectly valid JSON. Ensure all inner quotes inside strings are properly escaped to prevent Malformed JSON errors.
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