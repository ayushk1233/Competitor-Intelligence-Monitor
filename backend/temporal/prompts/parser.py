import json
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.temporal.models import TemporalAnalysis
from backend.temporal.exceptions import TemporalReasoningError
from backend.temporal.prompts.templates import TEMPORAL_PROMPT_VERSION

class TemporalResponseParser:
    """
    Parses and validates LLM JSON output against the TemporalAnalysis domain model.
    """
    
    def parse(self, response_text: str, company_name: str) -> TemporalAnalysis:
        # Strip potential markdown formatting (e.g. ```json ... ```)
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise TemporalReasoningError(f"Failed to parse LLM response as JSON: {e}")
            
        # Inject context not provided by LLM directly
        data["company_name"] = company_name
        data["analysis_timestamp"] = datetime.now(timezone.utc).isoformat()
        data["timeline_version"] = TEMPORAL_PROMPT_VERSION
        
        try:
            analysis = TemporalAnalysis(**data)
            return analysis
        except ValidationError as e:
            raise TemporalReasoningError(f"LLM output failed domain model validation: {e}")
