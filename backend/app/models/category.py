from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("id", "transaction_type", name="uq_categories_id_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(16), nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")
