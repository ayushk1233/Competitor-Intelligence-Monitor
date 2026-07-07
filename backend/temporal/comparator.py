import logging
from backend.memory.models import CompanyTimeline
from backend.temporal.models import TimelineComparison, ComparisonMetadata
from backend.temporal.exceptions import TimelineComparisonError

logger = logging.getLogger(__name__)

class TimelineComparator:
    """
    Transforms a CompanyTimeline into a structured TimelineComparison that is ready for reasoning.
    Operates purely on the already-retrieved CompanyTimeline without mutating it.
    """

    def compare(self, timeline: CompanyTimeline) -> TimelineComparison:
        if not timeline.events:
            raise TimelineComparisonError("Timeline contains 0 events. No history to analyze.")
        
        if len(timeline.events) == 1:
            raise TimelineComparisonError("Timeline contains 1 event. Change requires at least two observations.")
        
        # Timeline events should be chronologically ordered (oldest to newest)
        events = list(timeline.events) # Copy to ensure immutability
        
        latest_event = events[-1]
        previous_event = events[-2]
        historical_context = events[:-2]
        
        # Calculate metadata
        total_events = len(events)
        historical_depth = len(historical_context)
        
        days_between = (latest_event.analyzed_at - previous_event.analyzed_at).days
        timeline_span_days = (latest_event.analyzed_at - events[0].analyzed_at).days
        
        metadata = ComparisonMetadata(
            total_events=total_events,
            historical_depth=historical_depth,
            days_between_latest_and_previous=abs(days_between),
            timeline_span_days=abs(timeline_span_days)
        )
        
        comparison = TimelineComparison(
            company_name=timeline.company_name,
            latest_event=latest_event,
            previous_event=previous_event,
            historical_context=historical_context,
            metadata=metadata
        )
        
        logger.debug(
            "Constructed TimelineComparison",
            extra={
                "company": timeline.company_name,
                "total_events": total_events,
                "historical_events": historical_depth,
                "latest_run": latest_event.run_id,
                "previous_run": previous_event.run_id
            }
        )
        
        return comparison
