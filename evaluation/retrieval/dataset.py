import json
from pathlib import Path
from pydantic import BaseModel

class GoldenQuery(BaseModel):
    query: str
    company: str
    expected_runs: list[str]

class RetrievalDataset:
    def __init__(self, file_path: str = "evaluation_datasets/retrieval/golden_queries.json"):
        self.file_path = Path(file_path)
        
    def load(self) -> list[GoldenQuery]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.file_path}")
            
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [GoldenQuery(**item) for item in data]
