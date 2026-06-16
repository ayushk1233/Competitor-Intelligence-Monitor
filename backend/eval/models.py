from typing import List, Optional

from pydantic import BaseModel


class EvalExpectation(BaseModel):
    expected_tone: str
    momentum_min: int
    momentum_max: int

    expected_keywords: List[str]
    expected_icp_keywords: List[str]

    expected_company_concepts: List[str] = []
    expected_strategic_pass: List[str] = []
    expected_strategic_fail: List[str] = []


class EvalResult(BaseModel):
    company_name: str

    tone_match: bool
    momentum_in_range: bool

    keyword_overlap_score: float
    icp_recall_score: float
    
    extraction_score: float = 0.0
    intelligence_score: float = 0.0

    company_understanding_score: float = 0.0
    strategic_accuracy_score: float = 0.0
    confidence_calibration_score: float = 0.0
    false_negative_score: float = 0.0
    evidence_quality_score: float = 0.0

    overall_score: float

    actual_tone: str
    actual_momentum: int

    errors: Optional[List[str]] = None
from typing import Dict, Any

class ReplayResult(BaseModel):
    company_name: str
    
    # Pre-extraction metrics
    content_retention_ratio: float = 100.0
    noise_removed_count: int = 0
    cleaned_content_preview: str = ""
    removed_content_preview: List[str] = []
    
    # Extraction metrics
    signals_extracted: int = 0
    signals_preserved: int = 0
    signals_dropped: int = 0

    launch_signals: List[str] = []
    shipping_signals: List[str] = []
    adoption_signals: List[str] = []
    hiring_signals: List[str] = []
    partnership_signals: List[str] = []

    momentum_score: int = 0

    drop_reasons: List[str] = []
    routing_summary: Dict[str, Any] = {}
