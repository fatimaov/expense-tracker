"""Add minimal per-user AI provider request-start records.

Revision ID: d6e9b4c17a30
Revises: c9d1e4f2a7b0
"""
from alembic import op
import sqlalchemy as sa


revision = "d6e9b4c17a30"
down_revision = "c9d1e4f2a7b0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ai_request_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ai_request_attempts_user_started",
        "ai_request_attempts",
        ["user_id", "started_at"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_ai_request_attempts_user_started", table_name="ai_request_attempts")
    op.drop_table("ai_request_attempts")
