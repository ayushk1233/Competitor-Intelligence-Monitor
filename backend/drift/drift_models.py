from pydantic import BaseModel


class DriftReport(BaseModel):
    company_name: str

    old_momentum: int
    new_momentum: int

    momentum_delta: int

    added_keywords: list[str]
    removed_keywords: list[str]

    tone_changed: bool