"""Add the Layer 1 transaction and category foundation.

Revision ID: c9d2e41f6a7b
Revises: ad5a390c0763
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c9d2e41f6a7b"
down_revision = "ad5a390c0763"
branch_labels = None
depends_on = None


transaction_type = postgresql.ENUM(
    "income", "expense", name="transaction_type", create_type=False
)
buc_classification = postgresql.ENUM(
    "bill", "usage", "choice", name="buc_classification", create_type=False
)
reflective_context = postgresql.ENUM(
    "need", "love", "like", "want", name="reflective_context", create_type=False
)


def upgrade():
    bind = op.get_bind()
    transaction_type.create(bind, checkfirst=True)
    buc_classification.create(bind, checkfirst=True)
    reflective_context.create(bind, checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("transaction_type", transaction_type, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "transaction_type", name="uq_category_key_type"),
    )
    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("key", sa.String),
            sa.column("label", sa.String),
            sa.column("transaction_type", transaction_type),
        ),
        [
            {"key": "transport", "label": "Transport", "transaction_type": "expense"},
            {"key": "accommodation", "label": "Accommodation", "transaction_type": "expense"},
            {"key": "food", "label": "Food", "transaction_type": "expense"},
            {"key": "activities", "label": "Activities", "transaction_type": "expense"},
            {"key": "other", "label": "Other", "transaction_type": "expense"},
            {"key": "salary", "label": "Salary", "transaction_type": "income"},
            {"key": "other", "label": "Other", "transaction_type": "income"},
        ],
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", transaction_type, nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("b_u_c", buc_classification, nullable=True),
        sa.Column("reflective_context", reflective_context, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        sa.CheckConstraint(
            "transaction_type = 'expense' OR (b_u_c IS NULL AND reflective_context IS NULL)",
            name="ck_transactions_income_has_no_expense_context",
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_transaction_date", "transactions", ["transaction_date"])
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])

    # Preserve existing MVP expenses in the canonical transaction history. The
    # legacy table is retained until the expense API is adapted in the next slice.
    op.execute(
        """
        INSERT INTO transactions (
            id, user_id, transaction_type, amount, transaction_date,
            category_id, notes, created_at, updated_at
        )
        SELECT
            expenses.id,
            expenses.user_id,
            'expense',
            expenses.amount,
            expenses.expense_date,
            categories.id,
            expenses.notes,
            expenses.created_at AT TIME ZONE 'UTC',
            expenses.created_at AT TIME ZONE 'UTC'
        FROM expenses
        JOIN categories
          ON categories.transaction_type = 'expense'
         AND categories.label = expenses.category::text
        """
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('transactions', 'id'),
            COALESCE((SELECT MAX(id) FROM transactions), 1),
            true
        )
        """
    )


def downgrade():
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_index("ix_transactions_transaction_date", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("categories")

    bind = op.get_bind()
    reflective_context.drop(bind, checkfirst=True)
    buc_classification.drop(bind, checkfirst=True)
    transaction_type.drop(bind, checkfirst=True)
