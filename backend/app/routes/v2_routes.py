from pathlib import Path

from flask import Blueprint, jsonify, send_file
from flask_swagger_ui import get_swaggerui_blueprint

from ..services.transaction_service import list_categories


api_v2 = Blueprint("api_v2", __name__, url_prefix="/api/v2")
OPENAPI_PATH = Path(__file__).resolve().parents[1] / "openapi" / "v2.json"


@api_v2.get("/health")
def health_v2():
    return jsonify(status="ok")


@api_v2.get("/categories")
def categories_v2():
    return jsonify(categories=[
        {"key": category.key, "label": category.label, "transaction_type": category.transaction_type}
        for category in list_categories()
    ])


@api_v2.get("/openapi.json")
def openapi_v2():
    return send_file(OPENAPI_PATH, mimetype="application/json")


swagger_ui = get_swaggerui_blueprint(
    "/api/v2/docs",
    "/api/v2/openapi.json",
    config={"app_name": "Expense Tracker V2 API"},
)
