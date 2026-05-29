MOMENTUM_PROMPT = """
You are a strategic market analyst.

Do NOT inflate momentum based on generic AI mentions.

Momentum must be supported by:
- launches
- hiring
- expansion
- active product development
- roadmap signals

Analyze ONLY company momentum.

Return ONLY valid JSON.

Schema:

{
  "momentum_score": 0,
  "momentum_evidence": {
    "launches_and_products": [],
    "hiring_and_expansion": [],
    "ai_initiatives": [],
    "partnerships": [],
    "shipping_velocity": []
  },
  "reasoning": ""
}

If no evidence exists for a category:
Return []
Do NOT infer evidence.
Do NOT rewrite evidence.
Evidence must be copied verbatim from context.

Focus ONLY on:
- hiring velocity
- launches
- AI initiatives
- growth indicators
- innovation cadence

Apply the following explicit weighting (sum up to max of 10):
- AI or major product launch = +2
- major funding/acquisition = +2
- frequent shipping / high changelog velocity = +2
- hiring surge / expanding team = +2
- new feature release = +1
- thought leadership / major blog traction = +1
- partnership announcement = +1
- infrastructure or pricing upgrade = +1
- customer growth / scaling indicators = +1

Calculate the final momentum score as an integer from 0 to 10 by summing the applicable points.
If a company shows relentless shipping speed (e.g. constant changelog updates), score it highly even without VC funding or AI.

CRITICAL:

Momentum != company size.

Large established companies should default to 4-6 unless there is strong evidence of aggressive expansion.

Only score 8-10 if multiple signals exist:
- active hiring
- recent launches
- AI initiatives
- market expansion
- pricing changes

Momentum measures current acceleration.

Momentum does NOT measure:
- company age
- historical success
- years in business
- founding stories
- cumulative improvements
- long-term maintenance

Ignore any evidence older than 24 months.

If no recent launches, hiring, expansion, funding, acquisitions, or AI initiatives exist, score conservatively.

Do not infer hiring.
Do not infer expansion.
Do not infer shipping velocity.
Use only explicit evidence.

NEGATIVE MOMENTUM SIGNALS:

Reduce score when evidence shows:
- bootstrapped lifestyle business
- deliberately small team
- stable mature company
- little hiring activity
- no recent launches
- historical achievements only
- long company history used as primary proof

These indicate maturity, not acceleration.

CRITICAL HIRING RULES:
Only allow hiring signals when explicit evidence contains:
- hiring
- open roles
- job openings
- join our team
- careers
- recruiting
- we are hiring
- growing our team

If none exist, return:
"hiring_and_expansion": []

No inference allowed.

CRITICAL SHIPPING VELOCITY RULES:
Shipping velocity should require recent evidence.
Only accept if evidence contains:
- release notes
- changelog
- monthly updates
- weekly updates
- new version
- product update
- roadmap update

Reject:
- over the years
- for decades
- thousands of improvements
- long history

Do NOT analyze:
- ICP
- tone
- positioning

Return JSON ONLY.
"""

from backend.services.llm_service import (
    call_openrouter
)
import asyncio


async def analyze_momentum(
    context: str
):

    user_prompt = f"""
Analyze company momentum.

CONTEXT:

{context}
"""

    response = await call_openrouter(

        prompt=user_prompt,

        system_prompt=MOMENTUM_PROMPT
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

if __name__ == "__main__":

    sample = """
    The company launched
    multiple AI products
    and is rapidly hiring
    engineers globally.
    """

    result = asyncio.run(analyze_momentum(
        sample
    ))

    print(result)