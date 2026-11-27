"""resource_finder: locate campus and community support resources."""


from pydantic import BaseModel, Field


class ResourceInput(BaseModel):
    resource_type: str = Field(
        ...,
        description="Type of resource: counselling, health_clinic, peer_support, emergency, spiritual, legal_aid, other",
    )
    location: str | None = Field(
        None,
        description="Campus or area, e.g. 'main campus', 'hostel block B', 'town centre'",
    )
    hours: str | None = Field(
        None,
        description="Preferred hours, e.g. 'evening', 'weekend', '24 hours'",
    )


class ResourceResult(BaseModel):
    id: str
    name: str
    type: str
    location: str
    contact: str
    hours: str
    cost: str | None = None
    description: str


def find_resources(resource_type: str, location: str | None = None, hours: str | None = None) -> list[ResourceResult]:
    """Find campus and community support resources matching the student's need.

    Placeholder implementation. Replace with a live directory (e.g. university
    services API or a maintained resource database) before production.
    """
    catalogue = [
        ResourceResult(
            id="res-001",
            name="University Counselling Centre",
            type="counselling",
            location="Main Campus, Student Wellness Block",
            contact="+254 700 000 100 / counselling@university.ac.ke",
            hours="Mon-Fri 08:00-17:00",
            cost="Free for registered students",
            description="Confidential one-on-one counselling and group therapy for students.",
        ),
        ResourceResult(
            id="res-002",
            name="Campus Health Clinic",
            type="health_clinic",
            location="Main Campus, Health Centre",
            contact="+254 700 000 101",
            hours="Mon-Fri 07:30-16:30, Sat 08:00-12:00",
            cost="Subsidised for students",
            description="Primary care, mental health screening, and referrals.",
        ),
        ResourceResult(
            id="res-003",
            name="Peer Support Network",
            type="peer_support",
            location="Hostel blocks & online",
            contact="peersupport@university.ac.ke",
            hours="Evenings & weekends (volunteer-led)",
            cost="Free",
            description="Trained student peer supporters for informal, confidential conversations.",
        ),
        ResourceResult(
            id="res-004",
            name="National Mental Health Helpline",
            type="emergency",
            location="Nationwide (toll-free)",
            contact="1199",
            hours="24 hours / 7 days",
            cost="Free",
            description="Crisis helpline for mental health emergencies, operated by the Ministry of Health.",
        ),
        ResourceResult(
            id="res-005",
            name="Campus Security (Emergency)",
            type="emergency",
            location="Main Campus security desk",
            contact="+254 700 000 999",
            hours="24 hours / 7 days",
            cost="Free",
            description="24/7 campus security for immediate safety concerns.",
        ),
        ResourceResult(
            id="res-006",
            name="Legal Aid Clinic",
            type="legal_aid",
            location="Law School, Main Campus",
            contact="legalaid@university.ac.ke",
            hours="Tue-Thu 09:00-15:00",
            cost="Free for students",
            description="Free legal advice on tenancy, disciplinary, and family matters.",
        ),
    ]

    results = [r for r in catalogue if r.type == resource_type]
    if location:
        loc = location.lower()
        results = [r for r in results if loc in r.location.lower()]
    if hours:
        h = hours.lower()
        results = [r for r in results if h in r.hours.lower()]
    return results
