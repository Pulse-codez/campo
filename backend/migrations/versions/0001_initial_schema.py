"""Initial schema: tenants, users, consent, encrypted chats, peer support, audit.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID_DEFAULT = sa.text("gen_random_uuid()")
NOW = sa.text("now()")


def upgrade() -> None:
    # pgvector powers semantic knowledge retrieval for Claude's context.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "universities",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("email_domains", sa.String(512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_universities_slug", "universities", ["slug"], unique=False)
    op.create_index("ix_universities_public_id", "universities", ["public_id"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(32), nullable=False, server_default="student"),
        sa.Column("university_id", sa.Uuid(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("onboarded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("gender", sa.String(32), nullable=True),
        sa.Column("year_of_study", sa.Integer(), nullable=True),
        sa.Column("field_of_study", sa.String(32), nullable=False, server_default="other"),
        sa.Column("voice_preference", sa.String(16), nullable=False, server_default="auto"),
        sa.Column("emergency_contact_name", sa.String(255), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(32), nullable=True),
        sa.Column("university_other_name", sa.String(255), nullable=True),
        sa.Column("concerns", sa.String(255), nullable=True),
        sa.Column("therapist_key", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_university_id", "users", ["university_id"], unique=False)
    op.create_index("ix_users_public_id", "users", ["public_id"], unique=True)

    op.create_table(
        "consent_records",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("scope", sa.String(32), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("policy_version", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consent_records_user_id", "consent_records", ["user_id"], unique=False)

    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("anonymous_token_hash", sa.String(64), nullable=True),
        sa.Column("mode", sa.String(16), nullable=False, server_default="ai"),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("anonymous_token_hash"),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"], unique=False)
    op.create_index(
        "ix_conversations_anonymous_token_hash",
        "conversations",
        ["anonymous_token_hash"],
        unique=True,
    )
    op.create_index("ix_conversations_public_id", "conversations", ["public_id"], unique=True)

    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        # Bodies are AES-GCM ciphertext (`v1:...`) written by crypto_service.
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("risk_level", sa.String(32), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"], unique=False)
    op.create_index("ix_messages_public_id", "messages", ["public_id"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("target", sa.String(255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)

    op.create_table(
        "counselling_sessions",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("university_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("counsellor_id", sa.Uuid(), nullable=True),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("preferred_time", sa.String(255), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="requested"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["counsellor_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_counselling_sessions_university_id",
        "counselling_sessions",
        ["university_id"],
        unique=False,
    )
    op.create_index(
        "ix_counselling_sessions_student_id", "counselling_sessions", ["student_id"], unique=False
    )
    op.create_index(
        "ix_counselling_sessions_counsellor_id",
        "counselling_sessions",
        ["counsellor_id"],
        unique=False,
    )
    op.create_index(
        "ix_counselling_sessions_public_id", "counselling_sessions", ["public_id"], unique=True
    )

    op.create_table(
        "peer_matches",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("counterpart_conversation_id", sa.Uuid(), nullable=True),
        sa.Column("seeker_id", sa.Uuid(), nullable=True),
        sa.Column("peer_id", sa.Uuid(), nullable=True),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("field_of_study", sa.String(32), nullable=False, server_default="other"),
        sa.Column("year_of_study", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="searching"),
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["counterpart_conversation_id"], ["conversations.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["peer_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["seeker_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "conversation_id",
        "counterpart_conversation_id",
        "seeker_id",
        "peer_id",
        "field_of_study",
        "status",
        "public_id",
    ):
        op.create_index(
            f"ix_peer_matches_{column}",
            "peer_matches",
            [column],
            unique=column == "public_id",
        )

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=UUID_DEFAULT),
        sa.Column("public_id", sa.String(5), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("university_id", sa.Uuid(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_chunks_public_id", "knowledge_chunks", ["public_id"], unique=True)
    op.create_index("ix_knowledge_chunks_university_id", "knowledge_chunks", ["university_id"])
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_embedding "
        "ON knowledge_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_knowledge_chunks_embedding")
    for table in (
        "knowledge_chunks",
        "peer_matches",
        "counselling_sessions",
        "audit_logs",
        "messages",
        "conversations",
        "consent_records",
        "users",
        "universities",
    ):
        op.drop_table(table)
