from ..models import Expense


def serialize_expense(
    expense: Expense,
) -> dict[str, int | float | str | None]:
    return {
        "id": expense.id,
        "title": expense.title,
        "amount": float(expense.amount),
        "category": expense.category.value,
        "expense_date": expense.expense_date.isoformat(),
        "notes": expense.notes,
        "created_at": expense.created_at.isoformat(),
    }
