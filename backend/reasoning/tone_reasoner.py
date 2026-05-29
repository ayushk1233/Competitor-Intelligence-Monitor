TONE_PROMPT = """
You are a brand positioning analyst.

VERY important:

You MUST classify tone ONLY using explicit evidence from the provided context.

If evidence is weak or ambiguous:
- return "hybrid"

Do NOT infer enterprise positioning unless:
- enterprise messaging,
- compliance language,
- governance,
- scalability,
- or enterprise-specific terminology
is explicitly present.

Analyze ONLY the company's communication tone.

Return ONLY valid JSON.

Schema:

{
  "tone_classification": "",
  "signals": [],
  "evidence": [],
  "reasoning": ""
}

Focus on:
- branding language
- messaging style
- technical depth
- enterprise positioning
- visionary vs practical language
- startup vs enterprise communication

Classify tone as ONE of:

- technical
- enterprise
- visionary
- startup
- hybrid

CRITICAL CLASSIFICATION RULES:

Analyze the following indicators carefully:

Startup Indicators:
- fast-moving, building, founders, small team, careers, shipping, innovation

Technical Indicators:
- developer, api, sdk, infrastructure, engineering, platform

Enterprise Indicators:
- compliance, governance, security, large organizations, enterprise customers

Do NOT allow enterprise keywords alone to dominate if startup/technical indicators are strongly present.

If the company is a developer tool, coding assistant, or AI coding platform:
- Default to "technical" or "startup" UNLESS enterprise compliance/governance language is EXPLICITLY dominant.
- "AI", "developers", "code", "editor", "IDE" alone do NOT indicate enterprise.

If messaging uses casual, fast-moving, opinionated language:
- Classify as "startup" even if they mention enterprise customers.

If messaging is formal, compliance-heavy, governance-focused, Fortune-500 oriented:
- Classify as "enterprise".

If evidence does NOT clearly favor one category:
- Return "hybrid".

Do NOT default to "enterprise" when uncertain.
If uncertain → return "hybrid".

IMPORTANT:
- preserve messaging evidence
- preserve branding language
- preserve positioning examples

Do NOT analyze:
- momentum
- ICP
- growth
- hiring

Return JSON ONLY.
"""

from backend.services.llm_service import (
    call_openrouter
)


async def analyze_tone(
    context: str
):

    user_prompt = f"""
Analyze company communication tone.

CONTEXT:

{context}
"""

    response = await call_openrouter(

        prompt=user_prompt,

        system_prompt=TONE_PROMPT
    )

    response = response.strip()

    response = response.replace(
        "```json",
        ""
    )

    response = response.replace(
        "```",
        ""
    )

    return response.strip()

import asyncio


async def main():

    sample = """
    Our enterprise-grade AI platform
    helps developers build scalable
    infrastructure with advanced APIs.
    """

    result = await analyze_tone(
        sample
    )

    print(result)


if __name__ == "__main__":

    asyncio.run(main())