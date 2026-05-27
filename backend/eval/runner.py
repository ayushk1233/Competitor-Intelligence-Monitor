import asyncio
import time

from backend.eval.test_cases import TEST_CASES
from backend.eval.scorer import score_analysis
from backend.eval.report import generate_report

from backend.services.scraper_service import ScraperService
from backend.services.analysis_service import AnalysisService


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

    try:

        for test_case in TEST_CASES:

            company_name = test_case["company_name"]

            expectation = test_case["expectation"]

            result = await evaluate_company(
                scraper=scraper,
                analyzer=analyzer,
                company_name=company_name,
                expectation=expectation
            )

            results.append(result)

        report = generate_report(results)

        print("\n")
        print(report)

    finally:

        await scraper.close()

    duration = round(time.time() - start, 2)

    print(f"\nEvaluation suite completed in {duration}s")


if __name__ == "__main__":
    asyncio.run(run_evaluation_suite())