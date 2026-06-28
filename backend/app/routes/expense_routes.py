from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import Expense
from ..services.expense_service import create_expense, get_user_expenses
from ..services.validators import ValidationError


expense_bp = Blueprint("expenses", __name__, url_prefix="/api")


@expense_bp.post("/expenses")
@jwt_required()
def create_user_expense():
    try:
        user_id = _get_user_id()
        body = _get_json_body()
        expense = create_expense(
            user_id=user_id,
            amount=body.get("amount"),
            title=body.get("title"),
            expense_date=body.get("expense_date"),
            category=body.get("category"),
            notes=body.get("notes"),
        )
    except InvalidUserIdentityError as error:
        return jsonify(error=str(error)), 401
    except ValidationError as error:
        return jsonify(error=str(error)), 400

    return jsonify(expense=_expense_data(expense)), 201


@expense_bp.get("/expenses")
@jwt_required()
def list_user_expenses():
    try:
        user_id = _get_user_id()
    except InvalidUserIdentityError as error:
        return jsonify(error=str(error)), 401

    expenses = get_user_expenses(user_id)
    return jsonify(expenses=[_expense_data(expense) for expense in expenses])


class InvalidUserIdentityError(ValueError):
    """Raised when a valid token contains an unusable user identity."""


def _get_user_id() -> int:
    try:
        return int(get_jwt_identity())
    except (TypeError, ValueError):
        raise InvalidUserIdentityError(
            "Authorization token identity is invalid."
        ) from None


def _get_json_body() -> dict[str, object]:
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ValidationError("Request body must be a valid JSON object.")
    return body


def _expense_data(expense: Expense) -> dict[str, int | float | str | None]:
    return {
        "id": expense.id,
        "amount": float(expense.amount),
        "title": expense.title,
        "expense_date": expense.expense_date.isoformat(),
        "category": expense.category.value,
        "notes": expense.notes,
        "created_at": expense.created_at.isoformat(),
    }
