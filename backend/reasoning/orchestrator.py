import asyncio

from backend.reasoning.momentum_reasoner import (
    analyze_momentum
)

from backend.reasoning.tone_reasoner import (
    analyze_tone
)

from backend.reasoning.icp_reasoner import (
    analyze_icp
)

from backend.reasoning.synthesis_reasoner import (
    synthesize_intelligence
)

async def run_intelligence_pipeline(
    context: str
):

    # -----------------------------------
    # Run specialist agents concurrently
    # -----------------------------------

    (
        momentum_result,

        tone_result,

        icp_result

    ) = await asyncio.gather(

        analyze_momentum(context),

        analyze_tone(context),

        analyze_icp(context)
    )

    # -----------------------------------
    # Strategic synthesis
    # -----------------------------------

    final_result = await synthesize_intelligence(

        context=context,

        momentum_analysis=momentum_result,

        tone_analysis=tone_result,

        icp_analysis=icp_result
    )

    return {

        "momentum": momentum_result,

        "tone": tone_result,

        "icp": icp_result,

        "final": final_result
    }

async def main():

    sample = """
    The company launched
    multiple AI products
    and is rapidly hiring
    enterprise engineers.

    Their developer platform
    provides scalable APIs
    for enterprise customers.
    """

    result = await run_intelligence_pipeline(
        sample
    )

    print(result["final"])


if __name__ == "__main__":

    asyncio.run(main())