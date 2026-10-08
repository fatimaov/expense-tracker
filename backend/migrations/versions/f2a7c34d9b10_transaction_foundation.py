"""Replace MVP expenses with canonical transactions and fixed categories.

Revision ID: f2a7c34d9b10
Revises: ad5a390c0763
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f2a7c34d9b10"
down_revision = "ad5a390c0763"
branch_labels = None
depends_on = None


CATEGORIES = (
    ("expense_transport", "Transport", "expense"),
    ("expense_accommodation", "Accommodation", "expense"),
    ("expense_food", "Food", "expense"),
    ("expense_activities", "Activities", "expense"),
    ("expense_other", "Other", "expense"),
    ("income_salary", "Salary", "income"),
    ("income_other", "Other", "income"),
)


def upgrade():
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=64), nullable=False, unique=True),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("transaction_type", sa.String(length=16), nullable=False),
        sa.UniqueConstraint("id", "transaction_type", name="uq_categories_id_type"),
        sa.CheckConstraint("transaction_type IN ('expense', 'income')", name="ck_categories_transaction_type"),
    )
    categories = sa.table(
        "categories",
        sa.column("key", sa.String), sa.column("label", sa.String),
        sa.column("transaction_type", sa.String),
    )
    op.bulk_insert(categories, [
        {"key": key, "label": label, "transaction_type": kind}
        for key, label, kind in CATEGORIES
    ])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=16), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("transaction_type IN ('expense', 'income')", name="ck_transactions_type"),
        sa.CheckConstraint("amount > 0", name="ck_transactions_positive_amount"),
        sa.ForeignKeyConstraint(["category_id", "transaction_type"], ["categories.id", "categories.transaction_type"], name="fk_transactions_category_type"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name="fk_transactions_user_id_users"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_user_date", "transactions", ["user_id", "transaction_date"])

    bind = op.get_bind()
    bind.execute(sa.text("""
        INSERT INTO transactions
            (id, user_id, transaction_type, amount, transaction_date, category_id,
             notes, created_at, updated_at, deleted_at)
        SELECT e.id, e.user_id, 'expense', e.amount, e.expense_date, c.id,
               NULLIF(
                 CASE WHEN NULLIF(BTRIM(COALESCE(e.notes, '')), '') IS NULL
                      THEN BTRIM(e.title)
                      ELSE BTRIM(e.title) || CHR(10) || CHR(10) || BTRIM(e.notes)
                  END,
                  ''
               ),
               e.created_at AT TIME ZONE 'UTC',
               e.created_at AT TIME ZONE 'UTC',
               NULL
        FROM expenses e
        JOIN categories c ON c.key = CASE e.category::text
            WHEN 'Transport' THEN 'expense_transport'
            WHEN 'Accommodation' THEN 'expense_accommodation'
            WHEN 'Food' THEN 'expense_food'
            WHEN 'Activities' THEN 'expense_activities'
            WHEN 'Other' THEN 'expense_other'
        END
    """))
    op.drop_table("expenses")
    op.execute("DROP TYPE expense_category")
    op.execute("""SELECT setval(pg_get_serial_sequence('categories', 'id'), (SELECT MAX(id) FROM categories))""")
    op.execute("""SELECT setval(pg_get_serial_sequence('transactions', 'id'), COALESCE((SELECT MAX(id) FROM transactions), 1), EXISTS(SELECT 1 FROM transactions))""")


def downgrade():
    postgresql.ENUM(
        "Transport", "Accommodation", "Food", "Activities", "Other",
        name="expense_category",
    ).create(op.get_bind(), checkfirst=True)
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category", postgresql.ENUM("Transport", "Accommodation", "Food", "Activities", "Other", name="expense_category", create_type=False), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    bind = op.get_bind()
    bind.execute(sa.text("""
        INSERT INTO expenses (id, user_id, amount, title, expense_date, category, notes, created_at)
        SELECT t.id, t.user_id, t.amount, split_part(COALESCE(t.notes, ''), CHR(10) || CHR(10), 1),
               t.transaction_date, c.label::expense_category,
               NULLIF(substring(t.notes from position(CHR(10) || CHR(10) in COALESCE(t.notes, '')) + 2), ''),
               t.created_at AT TIME ZONE 'UTC'
        FROM transactions t JOIN categories c ON c.id = t.category_id
        WHERE t.transaction_type = 'expense'
    """))
    op.execute("SELECT setval(pg_get_serial_sequence('expenses', 'id'), COALESCE((SELECT MAX(id) FROM expenses), 1))")
    op.drop_index("ix_transactions_user_date", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("categories")
