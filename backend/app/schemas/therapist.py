"""Concern and virtual therapist schemas."""

from pydantic import BaseModel


class ConcernOut(BaseModel):
    key: str
    label: str


class TherapistOut(BaseModel):
    key: str
    name: str
    focus: str


class RecommendationOut(BaseModel):
    primary: TherapistOut
    alternatives: list[TherapistOut]
    show_crisis_resources: bool
