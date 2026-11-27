"""Add monthly reflections and kind notes.

Revision ID: 0002_checkin_kindness
Revises: 0001_initial_schema
Create Date: 2026-11-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_checkin_kindness"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID_DEFAULT = sa.text("gen_random_uuid()")
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "monthly_reflections",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("feelings", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_monthly_reflections_user_id", "monthly_reflections", ["user_id"], unique=False
    )
    op.create_index(
        "ix_monthly_reflections_public_id", "monthly_reflections", ["public_id"], unique=True
    )
    op.create_index(
        "uq_reflection_user_period",
        "monthly_reflections",
        ["user_id", "period"],
        unique=True,
    )

    op.create_table(
        "kind_notes",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("recipient", sa.String(120), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_kind_notes_user_id", "kind_notes", ["user_id"], unique=False)
    op.create_index("ix_kind_notes_public_id", "kind_notes", ["public_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_kind_notes_public_id", table_name="kind_notes")
    op.drop_index("ix_kind_notes_user_id", table_name="kind_notes")
    op.drop_table("kind_notes")

    op.drop_index("uq_reflection_user_period", table_name="monthly_reflections")
    op.drop_index("ix_monthly_reflections_public_id", table_name="monthly_reflections")
    op.drop_index("ix_monthly_reflections_user_id", table_name="monthly_reflections")
    op.drop_table("monthly_reflections")
