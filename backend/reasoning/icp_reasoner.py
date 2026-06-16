ICP_PROMPT = """
You are a go-to-market strategist.

You MUST infer ICP only from explicit customer, developer, platform, or enterprise evidence.

CRITICAL — "enterprise" guardrail:
Do NOT label the ICP as "enterprise" or "Enterprise IT teams" unless the source text explicitly contains words like "enterprise", "Fortune 500", "large organizations", "global corporations", or similar direct indicators.

Your goal is to provide a highly differentiated, specific breakdown of the Ideal Customer Profile.
Do not use generic labels like "developers" alone. Breakdown the ICP into Industry, Company Size, Buyer Persona, and User Persona.

Return ONLY valid JSON.

Schema:
{
  "industry": "",
  "company_size": "",
  "buyer": "",
  "user": "",
  "icp_keywords": [],
  "signals": [],
  "evidence": [],
  "reasoning": ""
}

Examples:

OpenAI:
industry: "cross-industry"
buyer: "founders, product leaders"
user: "developers, knowledge workers"

Anthropic:
industry: "regulated industries"
buyer: "CIO, CTO, AI governance leaders"
user: "engineering teams"

Google:
industry: "existing Google ecosystem"
buyer: "IT leaders, engineering managers"
user: "developers"

IMPORTANT:
- preserve customer targeting evidence
- preserve platform/developer clues
- preserve enterprise indicators (only if explicit)

Do NOT analyze momentum, branding tone, launches, or hiring.

Return JSON ONLY.
"""

from backend.services.llm_service import call_openrouter

async def analyze_icp(context: str):
    user_prompt = f"""
Analyze company ideal customer profile.

CONTEXT:
{context}
"""
    response = await call_openrouter(
        prompt=user_prompt,
        system_prompt=ICP_PROMPT,
        call_type="icp"
    )
    if not response:
        return "{}"
        
    response = response.strip()
    response = response.replace("```json", "").replace("```", "")
    return response.strip()

import asyncio

async def main():
    sample = "Our developer platform helps enterprise engineering teams build scalable AI applications."
    result = await analyze_icp(sample)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())