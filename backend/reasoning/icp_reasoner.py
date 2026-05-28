ICP_PROMPT = """
You are a go-to-market strategist.

Analyze ONLY the company's ideal customer profile (ICP).

Focus on:
- target customers
- company size
- technical vs non-technical users
- enterprise vs SMB focus
- developer focus
- industry targeting

Return ONLY:

1. icp_summary
2. reasoning (short paragraph)

Do NOT analyze:
- momentum
- branding tone
- launches
- hiring
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

    return response

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