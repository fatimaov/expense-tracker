from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import Category, Transaction
from .validators import ValidationError, validate_expense_date, validate_positive_amount, validate_required_string


CATEGORY_SEEDS = (
    ("expense_transport", "Transport", "expense"),
    ("expense_accommodation", "Accommodation", "expense"),
    ("expense_food", "Food", "expense"),
    ("expense_activities", "Activities", "expense"),
    ("expense_other", "Other", "expense"),
    ("income_salary", "Salary", "income"),
    ("income_other", "Other", "income"),
)
LEGACY_CATEGORY_KEYS = {
    "Transport": "expense_transport",
    "Accommodation": "expense_accommodation",
    "Food": "expense_food",
    "Activities": "expense_activities",
    "Other": "expense_other",
}


class TransactionNotFoundError(LookupError):
    pass


def list_categories(transaction_type: str | None = None) -> list[Category]:
    query = select(Category).order_by(Category.id)
    if transaction_type:
        query = query.where(Category.transaction_type == transaction_type)
    return list(db.session.scalars(query).all())


def get_category(key_or_label: object, transaction_type: str = "expense") -> Category:
    key = LEGACY_CATEGORY_KEYS.get(key_or_label, key_or_label)
    category = db.session.scalar(select(Category).where(
        Category.key == key,
        Category.transaction_type == transaction_type,
    ))
    if category is None:
        raise ValidationError("Category is invalid for this transaction type.")
    return category


def create_expense(user_id: int, amount: object, title: object, expense_date: object, category: object, notes: object = None) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        transaction_type="expense",
        amount=validate_positive_amount(amount),
        transaction_date=validate_expense_date(expense_date),
        category=get_category(category),
        notes=combine_title_and_notes(title, notes),
    )
    db.session.add(transaction)
    _commit()
    return transaction


def get_user_expenses(user_id: int) -> list[Transaction]:
    statement = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.deleted_at.is_(None),
    ).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
    return list(db.session.scalars(statement).all())


def get_expense_by_id(expense_id: int, user_id: int) -> Transaction | None:
    return db.session.scalar(select(Transaction).where(
        Transaction.id == expense_id,
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.deleted_at.is_(None),
    ))


def update_expense(expense_id: int, user_id: int, amount: object, title: object, expense_date: object, category: object, notes: object = None) -> Transaction:
    transaction = _get_owned_expense(expense_id, user_id)
    transaction.amount = validate_positive_amount(amount)
    transaction.notes = combine_title_and_notes(title, notes)
    transaction.transaction_date = validate_expense_date(expense_date)
    transaction.category = get_category(category)
    _commit()
    return transaction


def delete_expense(expense_id: int, user_id: int) -> None:
    transaction = _get_owned_expense(expense_id, user_id)
    transaction.deleted_at = datetime.now(timezone.utc)
    _commit()


def legacy_title_and_notes(transaction: Transaction) -> tuple[str, str | None]:
    value = (transaction.notes or "").strip()
    title, separator, notes = value.partition("\n\n")
    return (title, notes.strip() or None) if separator else (value, None)


def combine_title_and_notes(title: object, notes: object) -> str | None:
    cleaned_title = validate_required_string(title, "Title").strip()
    if notes is None:
        cleaned_notes = ""
    elif isinstance(notes, str):
        cleaned_notes = notes.strip()
    else:
        raise ValidationError("Notes must be a string.")
    combined = f"{cleaned_title}\n\n{cleaned_notes}" if cleaned_notes else cleaned_title
    return combined.strip() or None


def _get_owned_expense(expense_id: int, user_id: int) -> Transaction:
    transaction = get_expense_by_id(expense_id, user_id)
    if transaction is None:
        raise TransactionNotFoundError("Expense not found.")
    return transaction


def _commit() -> None:
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
