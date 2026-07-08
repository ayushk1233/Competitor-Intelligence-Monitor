import hashlib
import uuid
from backend.temporal.models import TemporalAnalysis, ReasoningContext
from backend.signals.models import StrategicSignal
from backend.signals.rules import calculate_severity, normalize_category

class StrategicSignalExtractor:
    """
    Converts TemporalAnalysis into deterministic, normalized StrategicSignal objects.
    """

    def _generate_fingerprint(self, company: str, category: str, direction: str, business_impact: str) -> str:
        """
        Generates a semantic fingerprint based on the core intelligence payload.
        This allows us to detect the same strategic signal over multiple runs.
        """
        payload = f"{company}:{category}:{direction}:{business_impact}".lower()
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _generate_signal_id(self, company: str, category: str, direction: str, run_id: str, summary: str) -> uuid.UUID:
        """
        Generates a deterministic UUIDv5 based on the specific run and observation.
        """
        NAMESPACE_CIM = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8') # generic namespace
        payload = f"{company}:{category}:{direction}:{run_id}:{summary}".lower()
        return uuid.uuid5(NAMESPACE_CIM, payload)

    def extract(self, analysis: TemporalAnalysis, context: ReasoningContext) -> list[StrategicSignal]:
        signals = []
        
        latest_run_id = context.comparison.latest_event.run_id
        
        for change in analysis.changes:
            norm_category = normalize_category(change.category.value)
            severity = calculate_severity(change.confidence_score)
            
            fingerprint = self._generate_fingerprint(
                company=analysis.company_name,
                category=norm_category.value,
                direction=change.direction.value,
                business_impact=change.business_impact
            )
            
            signal_id = self._generate_signal_id(
                company=analysis.company_name,
                category=norm_category.value,
                direction=change.direction.value,
                run_id=latest_run_id,
                summary=change.summary
            )
            
            signal = StrategicSignal(
                signal_id=signal_id,
                signal_fingerprint=fingerprint,
                company_name=analysis.company_name,
                category=norm_category,
                direction=change.direction,
                summary=change.summary,
                business_impact=change.business_impact,
                confidence_score=change.confidence_score,
                confidence_level=change.confidence_level,
                severity=severity,
                evidence=change.evidence,
                originating_run_id=latest_run_id,
                signal_source="temporal_engine",
                prompt_version=context.prompt_version,
                model_name=context.model_name,
                analysis_version=context.analysis_version,
                detected_at=analysis.analysis_timestamp
            )
            
            signals.append(signal)
            
        return signals
