ICP_PROMPT = """
You are a go-to-market strategist.

You MUST infer ICP only from explicit customer, developer, platform, or enterprise evidence.

Do NOT assume enterprise ICP without clear evidence.

Analyze ONLY the company's ideal customer profile (ICP).

Return ONLY valid JSON.

Schema:

{
  "icp_summary": "",
  "signals": [],
  "evidence": [],
  "reasoning": ""
}

Focus on:
- target customers
- company size
- technical vs non-technical users
- enterprise vs SMB focus
- developer focus
- industry targeting

IMPORTANT:
- preserve customer targeting evidence
- preserve platform/developer clues
- preserve enterprise indicators

Do NOT analyze:
- momentum
- branding tone
- launches
- hiring

Return JSON ONLY.
"""

from backend.services.llm_service import (
    call_openrouter
)


async def analyze_icp(
    context: str
):

    user_prompt = f"""
Analyze company ideal customer profile.

CONTEXT:

{context}
"""

    response = await call_openrouter(

        prompt=user_prompt,

        system_prompt=ICP_PROMPT
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
    Our developer platform helps
    enterprise engineering teams
    build scalable AI applications
    using advanced APIs.
    """

    result = await analyze_icp(
        sample
    )

    print(result)


if __name__ == "__main__":

    asyncio.run(main())