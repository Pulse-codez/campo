"""University schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UniversityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    domains: list[str]
