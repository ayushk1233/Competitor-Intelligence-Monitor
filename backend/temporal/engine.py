import time
import logging
from backend.memory.models import CompanyTimeline
from backend.temporal.models import TemporalComparisonResult, ReasoningContext
from backend.temporal.comparator import TimelineComparator
from backend.temporal.llm import TemporalLLM
from backend.temporal.exceptions import TimelineComparisonError, TemporalReasoningError
from backend.temporal.prompts.templates import TEMPORAL_PROMPT_VERSION

from backend.temporal.metrics import (
    temporal_reasoning_duration_seconds,
    temporal_reasoning_total,
    temporal_reasoning_failures_total
)

logger = logging.getLogger(__name__)

class TemporalEngine:
    """
    Orchestrates the temporal comparison and reasoning pipeline.
    Transforms a CompanyTimeline into a TemporalComparisonResult.
    """
    def __init__(self, comparator: TimelineComparator, llm: TemporalLLM, model_name: str = "anthropic/claude-3-haiku"):
        self._comparator = comparator
        self._llm = llm
        self._model_name = model_name

    async def analyze_timeline(self, timeline: CompanyTimeline) -> TemporalComparisonResult:
        start_time = time.time()
        company = timeline.company_name
        temporal_reasoning_total.labels(company=company).inc()
        
        try:
            # 1. Compare
            comparison = self._comparator.compare(timeline)
            
            # 2. Wrap in ReasoningContext
            context = ReasoningContext(
                comparison=comparison,
                prompt_version=TEMPORAL_PROMPT_VERSION,
                model_name=self._model_name,
                analysis_version="temporal-engine-v1"
            )
            
            # 3. Reason via LLM
            analysis = await self._llm.analyze(context)
            
            # 4. Return combined result
            result = TemporalComparisonResult(
                comparison=comparison,
                analysis=analysis
            )
            
            duration = time.time() - start_time
            temporal_reasoning_duration_seconds.labels(company=company).observe(duration)
            
            return result
            
        except TimelineComparisonError as e:
            temporal_reasoning_failures_total.labels(company=company, error_type="comparison_error").inc()
            logger.error(f"Timeline comparison failed for {company}: {e}")
            raise
        except TemporalReasoningError as e:
            temporal_reasoning_failures_total.labels(company=company, error_type="reasoning_error").inc()
            logger.error(f"Temporal reasoning failed for {company}: {e}")
            raise
        except Exception as e:
            temporal_reasoning_failures_total.labels(company=company, error_type="unexpected_error").inc()
            logger.error(f"Unexpected error during temporal analysis for {company}: {e}", exc_info=True)
            raise TemporalReasoningError(f"Unexpected error: {e}")
