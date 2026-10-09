"""Add optional expense context to transactions.

Revision ID: c9d1e4f2a7b0
Revises: b3faae81b7b4
"""
from alembic import op
import sqlalchemy as sa


revision = "c9d1e4f2a7b0"
down_revision = "b3faae81b7b4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("transactions", sa.Column("b_u_c", sa.String(length=16), nullable=True))
    op.add_column("transactions", sa.Column("reflective_context", sa.String(length=16), nullable=True))
    op.create_check_constraint(
        "ck_transactions_b_u_c",
        "transactions",
        "b_u_c IS NULL OR b_u_c IN ('bill', 'usage', 'choice')",
    )
    op.create_check_constraint(
        "ck_transactions_reflective_context",
        "transactions",
        "reflective_context IS NULL OR reflective_context IN ('need', 'love', 'like', 'want')",
    )
    op.create_check_constraint(
        "ck_transactions_context_expense_only",
        "transactions",
        "transaction_type = 'expense' OR (b_u_c IS NULL AND reflective_context IS NULL)",
    )


def downgrade():
    op.drop_constraint("ck_transactions_context_expense_only", "transactions", type_="check")
    op.drop_constraint("ck_transactions_reflective_context", "transactions", type_="check")
    op.drop_constraint("ck_transactions_b_u_c", "transactions", type_="check")
    op.drop_column("transactions", "reflective_context")
    op.drop_column("transactions", "b_u_c")
