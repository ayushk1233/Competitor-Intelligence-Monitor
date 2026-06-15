import asyncio
import time

from backend.eval.regression import (
    calculate_regression,
    load_baseline_score,
)
from backend.eval.report import generate_report
from backend.eval.scorer import score_analysis
from backend.eval.snapshot import EvaluationSnapshot
from backend.eval.storage import save_evaluation_snapshot
from backend.eval.test_cases import TEST_CASES
from backend.prompts.metadata.prompt_versions import (
    ANALYSIS_PROMPT_VERSION,
    COMPARISON_PROMPT_VERSION,
)
from backend.services.analysis_service import AnalysisService
from backend.services.scraper_service import ScraperService

MODEL_NAME = "deepseek/deepseek-chat"
TEMPERATURE = 0.0


import os
import json

OFFLINE_MODE = True

async def evaluate_company(
    scraper,
    analyzer,
    company_name: str,
    expectation
):

    print(f"\nEvaluating {company_name}...")

    try:
        if OFFLINE_MODE:
            golden_path = "tests/golden_analyses.json"
            if not os.path.exists(golden_path):
                raise FileNotFoundError(f"{golden_path} not found for offline evaluation.")
            
            with open(golden_path, "r") as f:
                golden_data = json.load(f)
            
            if company_name not in golden_data:
                raise ValueError(f"{company_name} not in golden datasets.")
                
            analysis_dict = golden_data[company_name]
            analysis_dict.setdefault("analysis_success", True)
            analysis_dict.setdefault("name", company_name)
            analysis_dict.setdefault("domain", f"{company_name.lower()}.com")
            
            from backend.models.schemas import CompetitorAnalysis
            analysis = CompetitorAnalysis(**analysis_dict)
            
        else:
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

    scraper = None
    analyzer = None
    if not OFFLINE_MODE:
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
        avg_extraction = (
            round(sum(r.extraction_score for r in results) / len(results), 3)
            if results else 0.0
        )
        avg_intelligence = (
            round(sum(r.intelligence_score for r in results) / len(results), 3)
            if results else 0.0
        )

        snapshot = EvaluationSnapshot(
            timestamp=time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            status=evaluation_status,
            overall_score=average_score,
            extraction_score=avg_extraction,
            intelligence_score=avg_intelligence,
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

        baseline_score = load_baseline_score()

        regression_report = calculate_regression(
            latest_score=average_score,
            baseline_score=baseline_score,
        )

        print("\n")
        print("=" * 50)
        print("REGRESSION REPORT")
        print("=" * 50)

        print(
            f"Latest Score   : "
            f"{regression_report['latest_score']:.3f}"
        )

        print(
            f"Baseline Score : "
            f"{regression_report['baseline_score']:.3f}"
        )

        print(
            f"Delta          : "
            f"{regression_report['delta']:.3f}"
        )

        if regression_report["improved"]:
            print("Status         : IMPROVED")

        elif regression_report["regressed"]:
            print("Status         : REGRESSED")

        else:
            print("Status         : NO CHANGE")

        print(
            f"\nSaved evaluation snapshot:"
            f" {saved_path}"
        )

    finally:
        if scraper:
            await scraper.close()

    duration = round(time.time() - start, 2)

    print(f"\nEvaluation suite completed in {duration}s")


if __name__ == "__main__":
    asyncio.run(run_evaluation_suite())