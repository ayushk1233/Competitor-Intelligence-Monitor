from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

from backend.eval.models import EvalResult


class EvaluationSnapshot(BaseModel):

    timestamp: str

    status: str

    overall_score: float

    llm_model: str

    temperature: float

    analysis_prompt_version: str

    comparison_prompt_version: str

    runtime_seconds: float

    results: List[EvalResult]

    failed_companies: List[str]

    failure_reasons: Dict[str, str]
