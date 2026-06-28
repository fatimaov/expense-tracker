from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import Expense
from .validators import (
    ValidationError,
    validate_expense_category,
    validate_expense_date,
    validate_positive_amount,
    validate_required_string,
)


class ExpenseNotFoundError(LookupError):
    """Raised when an expense is missing or does not belong to the user."""


def create_expense(
    user_id: int,
    amount: object,
    title: object,
    expense_date: object,
    category: object,
    notes: object = None,
) -> Expense:
    expense = Expense(
        user_id=user_id,
        amount=validate_positive_amount(amount),
        title=validate_required_string(title, "Title"),
        expense_date=validate_expense_date(expense_date),
        category=validate_expense_category(category),
        notes=_validate_optional_notes(notes),
    )
    db.session.add(expense)
    _commit()
    return expense


def get_user_expenses(user_id: int) -> list[Expense]:
    statement = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.expense_date.desc())
    )
    return list(db.session.scalars(statement).all())


def get_expense_by_id(expense_id: int, user_id: int) -> Expense | None:
    statement = select(Expense).where(
        Expense.id == expense_id,
        Expense.user_id == user_id,
    )
    return db.session.scalar(statement)


def update_expense(
    expense_id: int,
    user_id: int,
    amount: object,
    title: object,
    expense_date: object,
    category: object,
    notes: object = None,
) -> Expense:
    expense = _get_owned_expense(expense_id, user_id)
    expense.amount = validate_positive_amount(amount)
    expense.title = validate_required_string(title, "Title")
    expense.expense_date = validate_expense_date(expense_date)
    expense.category = validate_expense_category(category)
    expense.notes = _validate_optional_notes(notes)

    _commit()
    return expense


def delete_expense(expense_id: int, user_id: int) -> None:
    expense = _get_owned_expense(expense_id, user_id)
    db.session.delete(expense)
    _commit()


def _get_owned_expense(expense_id: int, user_id: int) -> Expense:
    expense = get_expense_by_id(expense_id, user_id)
    if expense is None:
        raise ExpenseNotFoundError("Expense not found.")
    return expense


def _validate_optional_notes(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError("Notes must be a string.")

    return value.strip() or None


def _commit() -> None:
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
