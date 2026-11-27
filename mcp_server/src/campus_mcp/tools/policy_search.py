"""policy_search — search campus support policies."""


from typing import Literal

from pydantic import BaseModel, Field

PolicyCategory = Literal[
    "mental_health",
    "academic_accommodation",
    "sexual_harassment",
    "financial_aid",
    "housing",
    "conduct",
    "other",
]


class PolicySearchInput(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="What the student is looking for, e.g. 'mental health leave of absence'",
    )
    category: PolicyCategory | None = Field(
        None,
        description="Policy category: mental_health, academic_accommodation, sexual_harassment, financial_aid, housing, conduct, other",
    )
    limit: int = Field(5, ge=1, le=20, description="Maximum number of results to return")


class PolicyResult(BaseModel):
    id: str
    title: str
    category: str
    summary: str
    url: str | None = None
    contact_email: str | None = None
    last_reviewed: str | None = None


def search_policies(query: str, category: str | None = None, limit: int = 5) -> list[PolicyResult]:
    """Search campus policies relevant to student wellbeing and support.

    This uses a static catalogue. Replace it with a real policy index (e.g. a
    document store or the university's policy API) before production.
    """
    params = PolicySearchInput(query=query, category=category, limit=limit)
    catalogue = [
        PolicyResult(
            id="pol-001",
            title="Mental Health Leave of Absence Policy",
            category="mental_health",
            summary="Students may request a leave of absence for mental health reasons with supporting documentation from a licensed clinician.",
            contact_email="counselling@university.ac.ke",
            last_reviewed="2025-09-01",
        ),
        PolicyResult(
            id="pol-002",
            title="Academic Accommodation for Health Reasons",
            category="academic_accommodation",
            summary="Reasonable accommodations including extended deadlines, alternative exam arrangements, and reduced course load.",
            contact_email="disability.services@university.ac.ke",
            last_reviewed="2025-06-15",
        ),
        PolicyResult(
            id="pol-003",
            title="Sexual Harassment & Gender-Based Violence Policy",
            category="sexual_harassment",
            summary="Reporting procedures, confidential support, and protection against retaliation for students who experience sexual harassment or GBV.",
            contact_email="safecampus@university.ac.ke",
            last_reviewed="2026-01-10",
        ),
        PolicyResult(
            id="pol-004",
            title="Financial Aid & Emergency Bursary",
            category="financial_aid",
            summary="Emergency bursaries and payment plan options for students experiencing financial hardship.",
            contact_email="financialaid@university.ac.ke",
            last_reviewed="2025-11-01",
        ),
        PolicyResult(
            id="pol-005",
            title="Student Housing & Welfare",
            category="housing",
            summary="On-campus housing assignments, off-campus accommodation support, and welfare checks for residents in distress.",
            contact_email="housing@university.ac.ke",
            last_reviewed="2025-08-20",
        ),
        PolicyResult(
            id="pol-006",
            title="Student Conduct & Disciplinary Process",
            category="conduct",
            summary="Rights and responsibilities during disciplinary proceedings, including the right to support and representation.",
            contact_email="deanofstudents@university.ac.ke",
            last_reviewed="2025-04-12",
        ),
    ]

    results = catalogue
    if params.category:
        results = [p for p in results if p.category == params.category]
    q = params.query.lower()
    results = [
        p
        for p in results
        if q in p.title.lower() or q in p.summary.lower() or q in p.category
    ]
    return results[: params.limit]
