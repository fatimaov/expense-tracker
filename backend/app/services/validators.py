import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from ..models import ExpenseCategory


MIN_PASSWORD_LENGTH = 8
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(ValueError):
    """Raised when service input fails validation."""


def validate_required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string.")

    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValidationError(f"{field_name} is required.")

    return cleaned_value


def validate_email(value: object) -> str:
    email = validate_required_string(value, "Email").lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValidationError("Email must be a valid email address.")

    return email


def validate_password(
    value: object,
    minimum_length: int = MIN_PASSWORD_LENGTH,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Password is required.")
    if len(value) < minimum_length:
        raise ValidationError(
            f"Password must be at least {minimum_length} characters long."
        )

    return value


def validate_positive_amount(value: object) -> Decimal:
    if isinstance(value, bool):
        raise ValidationError("Amount must be a valid number.")

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Amount must be a valid number.") from None

    if not amount.is_finite():
        raise ValidationError("Amount must be a finite number.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")

    return amount


def validate_expense_date(value: object) -> date:
    if isinstance(value, datetime):
        raise ValidationError("Expense date must use YYYY-MM-DD format.")
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValidationError("Expense date must use YYYY-MM-DD format.")

    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise ValidationError(
            "Expense date must be a valid date in YYYY-MM-DD format."
        ) from None


def validate_expense_category(value: object) -> ExpenseCategory:
    if isinstance(value, ExpenseCategory):
        return value
    if not isinstance(value, str):
        raise ValidationError("Expense category must be a string.")

    try:
        return ExpenseCategory(value.strip())
    except ValueError:
        valid_values = ", ".join(category.value for category in ExpenseCategory)
        raise ValidationError(
            f"Expense category must be one of: {valid_values}."
        ) from None
