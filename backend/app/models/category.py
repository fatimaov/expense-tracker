from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .enums import TransactionType

if TYPE_CHECKING:
    from .transaction import Transaction


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("key", "transaction_type", name="uq_category_key_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
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

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")
