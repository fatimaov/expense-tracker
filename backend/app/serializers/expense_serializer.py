from ..models import Transaction
from ..services.transaction_service import legacy_title_and_notes


def serialize_expense(
    expense: Transaction,
) -> dict[str, int | float | str | None]:
    title, notes = legacy_title_and_notes(expense)
    return {
        "id": expense.id,
        "title": title,
        "amount": float(expense.amount),
        "category": expense.category.label,
        "expense_date": expense.transaction_date.isoformat(),
        "notes": notes,
        "created_at": expense.created_at.isoformat(),
    }
