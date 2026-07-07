from backend.temporal.models import TimelineComparison
from backend.temporal.prompts.templates import TEMPORAL_PROMPT_VERSION, TEMPORAL_ANALYSIS_PROMPT

class TemporalPromptBuilder:
    """
    Transforms a TimelineComparison into a deterministic, structured prompt for the reasoning model.
    """
    
    def build(self, comparison: TimelineComparison) -> str:
        # Format historical context
        history_blocks = []
        if not comparison.historical_context:
            history_blocks.append("No historical context available.")
        else:
            for event in comparison.historical_context:
                block = f"[{event.run_id} - {event.analyzed_at}]\n"
                block += f"Executive Briefing: {event.executive_briefing or 'None'}\n"
                block += f"Structured Summary: {event.structured_summary or 'None'}\n"
                history_blocks.append(block)
                
        history_str = "\n".join(history_blocks)
        
        # Render the template
        prompt = TEMPORAL_ANALYSIS_PROMPT.format(
            total_events=comparison.metadata.total_events,
            historical_depth=comparison.metadata.historical_depth,
            days_between=comparison.metadata.days_between_latest_and_previous,
            span_days=comparison.metadata.timeline_span_days,
            
            latest_run_id=comparison.latest_event.run_id,
            latest_date=comparison.latest_event.analyzed_at.isoformat(),
            latest_briefing=comparison.latest_event.executive_briefing or 'None',
            latest_summary=comparison.latest_event.structured_summary or 'None',
            
            previous_run_id=comparison.previous_event.run_id,
            previous_date=comparison.previous_event.analyzed_at.isoformat(),
            previous_briefing=comparison.previous_event.executive_briefing or 'None',
            previous_summary=comparison.previous_event.structured_summary or 'None',
            
            historical_context=history_str
        )
        
        return prompt

    def get_version(self) -> str:
        return TEMPORAL_PROMPT_VERSION
