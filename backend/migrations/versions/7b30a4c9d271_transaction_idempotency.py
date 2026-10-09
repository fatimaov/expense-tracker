"""Persist replayable results for V2 transaction creation.

Revision ID: 7b30a4c9d271
Revises: f2a7c34d9b10
"""
from alembic import op
import sqlalchemy as sa


revision = "7b30a4c9d271"
down_revision = "f2a7c34d9b10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=36), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "key", name="uq_idempotency_user_key"),
    )


def downgrade():
    op.drop_table("idempotency_records")
