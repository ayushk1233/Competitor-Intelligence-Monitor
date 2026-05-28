MOMENTUM_PROMPT = """
You are a strategic market analyst.

Analyze ONLY the company momentum.

Focus on:
- hiring velocity
- launches
- AI initiatives
- product expansion
- growth indicators
- innovation cadence

Return ONLY:

1. momentum_score (1-10)
2. reasoning (short paragraph)

Do NOT analyze:
- ICP
- tone
- market positioning
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

    return response

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