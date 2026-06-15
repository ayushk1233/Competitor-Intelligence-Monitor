from typing import Dict, List

from pydantic import BaseModel

from backend.eval.models import EvalResult


class EvaluationSnapshot(BaseModel):

    timestamp: str

    status: str

    overall_score: float
    extraction_score: float = 0.0
    intelligence_score: float = 0.0

    llm_model: str

    temperature: float

    analysis_prompt_version: str

    comparison_prompt_version: str

    runtime_seconds: float

    results: List[EvalResult]

    failed_companies: List[str]

    failure_reasons: Dict[str, str]
