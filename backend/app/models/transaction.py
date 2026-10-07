from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .enums import BUCClassification, ReflectiveContext, TransactionType

if TYPE_CHECKING:
    from .category import Category
    from .user import User


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint(
            "transaction_type = 'expense' OR (b_u_c IS NULL AND reflective_context IS NULL)",
            name="ck_transactions_income_has_no_expense_context",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(
            TransactionType,
            name="transaction_type",
            values_callable=lambda transaction_types: [
                transaction_type.value for transaction_type in transaction_types
            ],
        ),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    b_u_c: Mapped[BUCClassification | None] = mapped_column(
        Enum(
            BUCClassification,
            name="buc_classification",
            values_callable=lambda classifications: [
                classification.value for classification in classifications
            ],
        ),
        nullable=True,
    )
    reflective_context: Mapped[ReflectiveContext | None] = mapped_column(
        Enum(
            ReflectiveContext,
            name="reflective_context",
            values_callable=lambda contexts: [context.value for context in contexts],
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship(back_populates="transactions")
