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

If evidence is absent, use one of:
- "No public evidence found" (for a section where content was available but no signal detected)
- "Insufficient information available" (for a section where the relevant page was not accessible)

Do NOT use "Not detected" — it sounds unprofessional.

FOR EVERY MAJOR SECTION you MUST provide:
- extracted_value (the analytical conclusion)
- evidence (a verbatim quote or specific observation from the content that supports this conclusion)
- source (which page/section the evidence came from, e.g. "homepage", "pricing page", "about page")
- confidence (integer 0–100 — how certain you are based on evidence strength)

Confidence calibration:
- 90-100: Direct statement from official source (e.g., pricing page shows "$29/month")
- 70-89: Strongly implied by multiple pieces of evidence
- 50-69: Reasonable inference from available content
- 30-49: Weak signal or ambiguous wording
- 0-29: No evidence, educated guess only

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
  "core_offering_evidence": ["verbatim quote from content supporting this"],
  "core_offering_source": "homepage",
  "core_offering_confidence": 92,
  "icp": "Synthesize from the ICP analysis",
  "icp_keywords": ["preserve", "directly", "from", "icp", "analysis"],
  "icp_evidence": ["preserve", "directly", "from", "icp", "analysis"],
  "icp_confidence": 88,
  "messaging_tone": "Pick exactly one: enterprise | startup | technical | visionary | hybrid (from Tone analysis)",
  "tone_evidence": ["preserve", "directly", "from", "tone", "analysis"],
  "tone_confidence": 85,
  "pricing_signals": "Extract from context. Use 'No public evidence found' if unavailable.",
  "pricing_evidence": [],
  "pricing_source": "",
  "pricing_confidence": 0,
  "hiring_signals": "Extract from context. Use 'No public evidence found' if unavailable.",
  "hiring_evidence": [],
  "hiring_source": "",
  "hiring_confidence": 0,
  "recent_launches": ["extract", "from", "context", "or", "momentum", "analysis"],
  "strategic_keywords": ["extract", "from", "context. Extract recurring business themes. Examples: enterprise, payments, AI, automation, developer platform, CRM, compliance, workflow. Only include terms that appear multiple times or represent strategic focus. Avoid generic words."],
  "keywords_evidence": [],
  "keywords_confidence": 75,
  "growth_signals": ["extract", "from", "context", "or", "momentum", "analysis"],
  "risk_flags": ["extract", "from", "context"],
  "momentum_score": 7,
  "momentum_evidence": ["preserve", "directly", "from", "momentum", "analysis"],
  "momentum_negative_factors": ["list negative factors like: No recent product launches", "No hiring activity", "No partnership signals detected"],
  "momentum_reasoning": "Brief explanation of why this momentum score was assigned, referencing specific signals",
  "analyst_note": "Summary: What the company does in one sentence.\n\nStrength: Their single biggest advantage.\n\nRisk: Their most significant vulnerability.\n\nOutlook: 1-2 sentence forward-looking assessment."
}

analyst_note FORMAT REQUIREMENTS (max 150 words total):
You MUST format as EXACTLY:
Summary: <one sentence>

Strength: <one sentence>

Risk: <one sentence>

Outlook: <1-2 sentences>

Do NOT invent new interpretations.
Do NOT override specialist agents.
Assemble conservatively.
CRITICAL: You MUST return perfectly valid JSON. Ensure all inner quotes inside strings are properly escaped to prevent Malformed JSON errors.
"""
from backend.services.llm_service import call_openrouter


async def synthesize_intelligence(

    context: str,

    momentum_analysis: str,

    tone_analysis: str,

    icp_analysis: str,

    validation: dict = None
):

    validation_block = ""
    if validation:
        validation_block = f"""
[COMPANY VALIDATION — Must respect this]
Company: {validation.get('company_name', 'Unknown')}
Description: {validation.get('company_description', 'Unknown')}
Category: {validation.get('category', 'Unknown')}
Product Type: {validation.get('product_type', 'Unknown')}
Primary Use Case: {validation.get('primary_use_case', 'Unknown')}
Confidence Warning: {validation.get('validation_warning', False)}

CRITICAL: The validation above represents the best understanding of what this company actually is.
Your synthesis MUST be consistent with this validation.
If validation says this is NOT an IT services or consulting company, do NOT classify it as one.
"""

    user_prompt = f"""
SYNTHESIZE THESE ANALYSES AND CONTEXT:{validation_block}

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