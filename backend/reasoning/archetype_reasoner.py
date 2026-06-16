ARCHETYPE_PROMPT = """
You are a strategic archetype analyst.

Your job is to identify WHY companies behave the way they do, taking their raw intelligence and interpreting their fundamental business identity.

Input will include:
- Tone Analysis
- ICP Analysis
- Strategic Interpretation
- Momentum / Signals
- Analyst Note (if any)

Choose the MOST ACCURATE Strategic Archetype from this controlled list:
- AI Platform Builder (Traits: ecosystem expansion, developer adoption, platform lock-in, marketplace strategy)
- Trusted Enterprise AI (Traits: governance, compliance, safety, regulated industries)
- AI Distribution Platform (Traits: leverage installed user base, cross-product integration, ecosystem dominance)
- Enterprise Workflow Platform (Traits: enterprise expansion, operational efficiency, workflow ownership)
- SMB Growth Platform (Traits: product-led growth, accessibility, adoption velocity)

If none perfectly fit, choose the closest or invent a highly descriptive similar archetype.

Return ONLY valid JSON.

Schema:
{
  "archetype": "The chosen archetype",
  "growth_model": "How they grow (e.g. Developer ecosystem expansion, Governance-led adoption)",
  "primary_moat": "What protects them (e.g. Platform lock-in, Installed user base, Trust and safety)",
  "strategic_risk": "Where they are vulnerable (e.g. Execution complexity, Distribution disadvantage)",
  "likely_next_moves": [
    {
      "hypothesis": "What they will do next",
      "confidence": "high|medium|low"
    }
  ]
}

Focus on generating structured hypothesis for future moves.
Return JSON ONLY.
"""

from backend.services.llm_service import call_openrouter

async def analyze_archetype(
    tone_output: str,
    icp_output: str,
    strategy_output: str,
    momentum_output: str
):
    user_prompt = f"""
Analyze the company's strategic archetype based on the following intelligence:

TONE ANALYSIS:
{tone_output}

ICP ANALYSIS:
{icp_output}

STRATEGIC INTERPRETATION:
{strategy_output}

MOMENTUM SIGNALS:
{momentum_output}
"""
    response = await call_openrouter(
        prompt=user_prompt,
        system_prompt=ARCHETYPE_PROMPT,
        call_type="archetype"
    )
    if not response:
        return "{}"
        
    response = response.strip()
    response = response.replace("```json", "").replace("```", "")
    return response.strip()
