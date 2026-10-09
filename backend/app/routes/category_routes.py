from flask import Blueprint, jsonify

from ..services.transaction_service import list_categories


category_bp = Blueprint("categories", __name__, url_prefix="/api")


@category_bp.get("/categories")
def get_categories():
    categories = [
        {
            "key": {
                "Transport": "TRANSPORT",
                "Accommodation": "ACCOMMODATION",
                "Food": "FOOD",
                "Activities": "ACTIVITIES",
                "Other": "OTHER",
            }[category.label],
            "label": category.label,
            "value": category.label,
        }
        for category in list_categories("expense")
    ]
    return jsonify(categories=categories)
