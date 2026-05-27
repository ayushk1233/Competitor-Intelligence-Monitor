from typing import List, Optional
from pydantic import BaseModel


class EvalExpectation(BaseModel):
    expected_tone: str
    momentum_min: int
    momentum_max: int

    expected_keywords: List[str]
    expected_icp_keywords: List[str]


class EvalResult(BaseModel):
    company_name: str

    tone_match: bool
    momentum_in_range: bool

    keyword_overlap_score: float
    icp_recall_score: float

    overall_score: float

    actual_tone: str
    actual_momentum: int

    errors: Optional[List[str]] = None