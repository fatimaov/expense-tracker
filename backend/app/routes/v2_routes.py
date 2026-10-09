from pathlib import Path

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_swagger_ui import get_swaggerui_blueprint

from ..services.transaction_service import create_transaction, list_categories
from ..utils import error_response


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


@api_v2.post("/transactions")
@jwt_required()
def create_transaction_v2():
    try:
        payload = request.get_json(silent=True)
        response_body, status_code = create_transaction(
            int(get_jwt_identity()),
            payload,
            request.headers.get("Idempotency-Key"),
        )
    except ValueError as error:
        fields = getattr(error, "fields", None)
        code = "VALIDATION_ERROR"
        if "Idempotency-Key" in (fields or {}):
            code = "IDEMPOTENCY_KEY_REQUIRED"
        return error_response(str(error), code, 400, fields)

    return jsonify(response_body), status_code


@api_v2.get("/openapi.json")
def openapi_v2():
    return send_file(OPENAPI_PATH, mimetype="application/json")


swagger_ui = get_swaggerui_blueprint(
    "/api/v2/docs",
    "/api/v2/openapi.json",
    config={"app_name": "Expense Tracker V2 API"},
)
