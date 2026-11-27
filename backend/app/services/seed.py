"""Seed Kenyan universities for the auth layer.

Email domains are placeholders to be verified with each institution before pilot use.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.university import University

SEED_UNIVERSITIES = [
    {"name": "University of Nairobi (UON)", "slug": "uon", "email_domains": "uonbi.ac.ke"},
    {"name": "Kenya Christian University (KCA)", "slug": "kca", "email_domains": "kca.ac.ke"},
    {"name": "Strathmore University", "slug": "strathmore", "email_domains": "strathmore.edu"},
    {"name": "Technical University of Kenya (TUK)", "slug": "tuk", "email_domains": "tukenya.ac.ke"},
    {"name": "Zetech University", "slug": "zetech", "email_domains": "zetech.ac.ke"},
    {"name": "Daystar University", "slug": "daystar", "email_domains": "daystar.ac.ke"},
    {"name": "Riara University", "slug": "riara", "email_domains": "riarauniversity.ac.ke"},
    {"name": "Kenyatta University (KU)", "slug": "ku", "email_domains": "ku.ac.ke"},
    {"name": "Moi University", "slug": "mu", "email_domains": "mu.ac.ke"},
    {
        "name": "Jomo Kenyatta University of Agriculture and Technology",
        "slug": "jkuat",
        "email_domains": "jkuat.ac.ke",
    },
    {"name": "Egerton University", "slug": "egerton", "email_domains": "egerton.ac.ke"},
    # Students whose university is not listed. Their email must end in .ac.ke or .edu, and an
    # admin must verify the account before it is trusted (not built yet).
    {"name": "Other (not listed)", "slug": "other", "email_domains": ""},
]


async def seed_universities(db: AsyncSession) -> None:
    for item in SEED_UNIVERSITIES:
        exists = await db.scalar(select(University.id).where(University.slug == item["slug"]))
        if exists is None:
            db.add(University(**item))
    await db.commit()
