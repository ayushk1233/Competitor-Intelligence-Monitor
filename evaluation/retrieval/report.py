import json
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel

class EvaluationReport(BaseModel):
    timestamp: str
    dataset_size: int
    recall_at_1: float
    recall_at_3: float
    recall_at_5: float
    mrr: float
    average_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    max_latency_ms: float
    company_filter_accuracy: float
    timeline_order_accuracy: float
    duplicate_rate: float

    def save(self, output_dir: str = "evaluation_runs/retrieval"):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/report_{timestamp_str}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)
            
        return filename
