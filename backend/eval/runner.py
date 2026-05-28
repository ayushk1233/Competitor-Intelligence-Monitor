import asyncio
import time

from backend.eval.test_cases import TEST_CASES
from backend.eval.scorer import score_analysis
from backend.eval.report import generate_report

from backend.services.scraper_service import ScraperService
from backend.services.analysis_service import AnalysisService
from backend.prompts.metadata.prompt_versions import (
    ANALYSIS_PROMPT_VERSION,
    COMPARISON_PROMPT_VERSION
)
from backend.eval.snapshot import (
    EvaluationSnapshot
)

from backend.eval.storage import (
    save_evaluation_snapshot
)

MODEL_NAME = "deepseek/deepseek-chat"
TEMPERATURE = 0.0


async def evaluate_company(
    scraper: ScraperService,
    analyzer: AnalysisService,
    company_name: str,
    expectation
):

    print(f"\nEvaluating {company_name}...")

    try:

        # -----------------------------------
        # Stage 1 — Scrape
        # -----------------------------------

        competitor_pages = await scraper.fetch_competitor(
            company_name
        )

        # -----------------------------------
        # Stage 2 — Analyze
        # -----------------------------------

        analysis = await analyzer.analyze_competitor(
            competitor_pages
        )

        # -----------------------------------
        # Stage 3 — Score
        # -----------------------------------

        result = score_analysis(
            analysis,
            expectation
        )

        return result

    except Exception as e:

        print(
            f"Evaluation failed for "
            f"{company_name}: {e}"
        )

        raise


async def run_evaluation_suite():

    start = time.time()

    print("\nRunning evaluation suite...\n")

    scraper = ScraperService()
    analyzer = AnalysisService()

    results = []
    failed_companies = []
    failure_reasons = {}

    try:

        for test_case in TEST_CASES:

            company_name = test_case["company_name"]

            expectation = test_case["expectation"]

            try:
                result = await evaluate_company(
                    scraper=scraper,
                    analyzer=analyzer,
                    company_name=company_name,
                    expectation=expectation
                )
                results.append(result)
            except Exception as e:
                print(f"Skipping failed company: {e}")
                failed_companies.append(company_name)
                failure_reasons[company_name] = str(e)

        if len(results) == 0:
            evaluation_status = "provider_failure"
        elif len(results) < len(TEST_CASES):
            evaluation_status = "partial_failure"
        else:
            evaluation_status = "success"

        duration = round(time.time() - start, 2)
        report = generate_report(
            results=results,
            status=evaluation_status,
            llm_model=MODEL_NAME,
            temperature=TEMPERATURE,
            analysis_prompt_version=ANALYSIS_PROMPT_VERSION,
            comparison_prompt_version=COMPARISON_PROMPT_VERSION,
            runtime_seconds=duration
        )

        print("\n")
        print(report)

        average_score = (
            round(sum(r.overall_score for r in results) / len(results), 3)
            if results else 0.0
        )

        snapshot = EvaluationSnapshot(
            timestamp=time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            status=evaluation_status,
            overall_score=average_score,
            llm_model=MODEL_NAME,
            temperature=TEMPERATURE,
            analysis_prompt_version=(
                ANALYSIS_PROMPT_VERSION
            ),
            comparison_prompt_version=(
                COMPARISON_PROMPT_VERSION
            ),
            runtime_seconds=duration,
            results=results,
            failed_companies=failed_companies,
            failure_reasons=failure_reasons
        )

        saved_path = save_evaluation_snapshot(
            snapshot
        )

        print(
            f"\nSaved evaluation snapshot:"
            f" {saved_path}"
        )

    finally:

        await scraper.close()

    duration = round(time.time() - start, 2)

    print(f"\nEvaluation suite completed in {duration}s")


if __name__ == "__main__":
    asyncio.run(run_evaluation_suite())