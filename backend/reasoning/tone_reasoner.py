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