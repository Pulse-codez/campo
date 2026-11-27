"""University schemas."""

from pydantic import BaseModel, ConfigDict

from app.models.university import University


class UniversityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    domains: list[str]

    @classmethod
    def from_university(cls, university: University) -> "UniversityOut":
        return cls(
            id=university.public_id,
            name=university.name,
            slug=university.slug,
            domains=university.domains,
        )
