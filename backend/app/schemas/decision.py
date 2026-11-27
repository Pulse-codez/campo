"""Decision lab schemas."""


from pydantic import BaseModel, Field


class Option(BaseModel):
    id: str
    label: str
    pros: list[str]
    cons: list[str]
    estimated_effort: str | None = None
    estimated_cost: str | None = None


class DecisionLabRequest(BaseModel):
    situation: str = Field(..., min_length=1, max_length=5000)
    options: list[Option] = Field(..., min_items=2, max_items=10)
    values: list[str] = Field(..., min_items=1, max_items=10)
