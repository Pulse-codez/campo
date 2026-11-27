"""Seed Kenyan universities for the auth layer.

Email domains are placeholders to be verified with each institution before pilot use.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.university import University

SEED_UNIVERSITIES = [
    {"name": "University of Nairobi", "slug": "uon", "email_domains": "uonbi.ac.ke"},
    {"name": "Kenyatta University", "slug": "ku", "email_domains": "ku.ac.ke"},
    {"name": "Moi University", "slug": "mu", "email_domains": "mu.ac.ke"},
    {
        "name": "Jomo Kenyatta University of Agriculture and Technology",
        "slug": "jkuat",
        "email_domains": "jkuat.ac.ke",
    },
    {"name": "Egerton University", "slug": "egerton", "email_domains": "egerton.ac.ke"},
    {"name": "Strathmore University", "slug": "strathmore", "email_domains": "strathmore.edu"},
]


async def seed_universities(db: AsyncSession) -> None:
    for item in SEED_UNIVERSITIES:
        exists = await db.scalar(select(University.id).where(University.slug == item["slug"]))
        if exists is None:
            db.add(University(**item))
    await db.commit()
