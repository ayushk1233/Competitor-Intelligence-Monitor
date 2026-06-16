TONE_PROMPT = """
You are a strategic brand positioning analyst.

Your goal is to identify the company's STRATEGIC TONE and positioning, rather than just using generic labels like "technical" or "enterprise".

Identify a PRIMARY and SECONDARY strategic tone from the following richer internal reasoning framework:

- Developer-First
- Enterprise-First
- Safety-First
- Commercialization-First
- Platform Ecosystem
- Infrastructure Layer
- Research-Led
- Compliance-Led
- Community-Led
- Product-Led Growth
- Distribution-Led

Analyze ONLY the company's communication tone and positioning strategy using explicit evidence from the provided context.

Return ONLY valid JSON.

Schema:
{
  "primary_tone": "",
  "secondary_tone": "",
  "signals": [],
  "evidence": [],
  "reasoning": ""
}

Examples of strategic positioning:

OpenAI:
Primary: Commercialization-First
Secondary: Developer Platform
Evidence: Enterprise partnerships, Academy, Deployment Company

Anthropic:
Primary: Safety-First Enterprise
Secondary: Research-Led
Evidence: Institute, Glasswing, Regulated industries

Google:
Primary: Platform Ecosystem
Secondary: Distribution-Led
Evidence: Chrome, Android, Workspace, Gemini rollout

CRITICAL RULES:
- Do NOT use old generic labels like "technical" or "startup".
- Extract specific evidence for WHY you chose these strategic tones.
- Do NOT infer enterprise positioning unless explicit enterprise/compliance language is present.
- Focus on branding language, messaging style, and market positioning.

Return JSON ONLY.
"""

from backend.services.llm_service import call_openrouter

async def analyze_tone(context: str):
    user_prompt = f"""
Analyze company communication tone and strategic positioning.

CONTEXT:
{context}
"""
    response = await call_openrouter(
        prompt=user_prompt,
        system_prompt=TONE_PROMPT,
        call_type="tone"
    )
    if not response:
        return "{}"
        
    response = response.strip()
    response = response.replace("```json", "").replace("```", "")
    return response.strip()

import asyncio

async def main():
    sample = "Our enterprise-grade AI platform helps developers build scalable infrastructure."
    result = await analyze_tone(sample)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())