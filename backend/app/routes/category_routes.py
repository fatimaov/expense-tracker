from flask import Blueprint, jsonify

from ..models import ExpenseCategory


category_bp = Blueprint("categories", __name__, url_prefix="/api")


@category_bp.get("/categories")
def get_categories():
    categories = [
        {
            "key": category.name,
            "label": category.value,
            "value": category.value,
        }
        for category in ExpenseCategory
    ]
    return jsonify(categories=categories)
