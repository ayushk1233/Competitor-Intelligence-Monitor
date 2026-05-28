TONE_PROMPT = """
You are a brand positioning analyst.

Analyze ONLY the company's communication tone.

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

Return ONLY:

1. tone_classification
2. reasoning (short paragraph)

Do NOT analyze:
- momentum
- ICP
- growth
- hiring
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

    return response

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