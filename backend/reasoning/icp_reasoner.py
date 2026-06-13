ICP_PROMPT = """
You are a go-to-market strategist.

You MUST infer ICP only from explicit customer, developer, platform, or enterprise evidence.

CRITICAL — "enterprise" guardrail:
Do NOT label the ICP as "enterprise" or "Enterprise IT teams" unless the source text explicitly contains words like "enterprise", "Fortune 500", "large organizations", "global corporations", or similar direct indicators.
If the text only mentions "developers", "teams", "companies", or "businesses", infer SMB/startup/developer ICP — do NOT default to enterprise.
"Enterprise" is a specific segment — do not over-infer it.

Analyze ONLY the company's ideal customer profile (ICP).

Return ONLY valid JSON.

ICP Extraction Rules:

Identify the primary customer segment.

Return concise labels such as:
- SMB teams
- Startups
- Developers
- Individual developers
- Engineering teams
- Enterprise IT teams (ONLY if explicitly supported)
- Product managers
- Marketing teams
- Financial institutions

Base the answer on explicit messaging evidence.
If evidence is thin, use "likely <segment>" — e.g. "likely SMB teams" — and reduce confidence.

Do not describe the product.
Do not return full sentences.

Schema:

{
  "icp_summary": "...",
  "icp_keywords": [
    "developers",
    "engineering teams",
    "enterprise"
  ],
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
- preserve enterprise indicators (only if explicit)

Do NOT analyze:
- momentum
- branding tone
- launches
- hiring

Return JSON ONLY.
"""

from backend.services.llm_service import call_openrouter


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