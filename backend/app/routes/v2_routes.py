from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_swagger_ui import get_swaggerui_blueprint

from ..services.transaction_service import (
    StaleTransactionError,
    TransactionForbiddenError,
    TransactionNotFoundError,
    create_transaction,
    delete_transaction,
    get_transaction,
    list_categories,
    list_transactions,
    serialize_created_transaction,
    update_transaction,
)
from ..services.assisted_entry_service import create_text_transaction_draft
from ..services.ai_request_guard import record_provider_request_start
from ..ai.config import AISettings
from ..ai.errors import (
    AIConfigurationError,
    AIRateLimitExceededError,
    AIProviderResponseError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIUnsupportedSchemaError,
)
from ..ai.factory import create_json_generator
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


@api_v2.post("/assisted-entry/text")
@jwt_required()
def create_text_draft_v2():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) != {"text"}:
        return error_response("Provide transaction text.", "VALIDATION_ERROR", 400, {"text": "Enter a transaction description."})
    text = payload["text"]
    if not isinstance(text, str) or not text.strip():
        return error_response("Transaction text is required.", "VALIDATION_ERROR", 400, {"text": "Enter a transaction description."})
    if len(text) > 1000:
        return error_response("Transaction text is too long.", "VALIDATION_ERROR", 400, {"text": "Use 1,000 characters or fewer."})

    try:
        settings = AISettings.from_mapping(current_app.config)
        generator = create_json_generator(settings)
        record_provider_request_start(int(get_jwt_identity()))
        result = create_text_transaction_draft(text, generator)
    except AIRateLimitExceededError as error:
        return error_response(str(error), "RATE_LIMIT_EXCEEDED", 429)
    except AIProviderTimeoutError as error:
        return error_response(str(error), "AI_PROVIDER_TIMEOUT", 504)
    except AIProviderResponseError as error:
        return error_response(str(error), "AI_PROVIDER_INVALID_RESPONSE", 502)
    except AIProviderUnavailableError as error:
        return error_response(str(error), "AI_PROVIDER_UNAVAILABLE", 503)
    except AIConfigurationError as error:
        return error_response(str(error), "AI_CONFIGURATION_ERROR", 503)
    except AIUnsupportedSchemaError as error:
        return error_response(str(error), "AI_CONFIGURATION_ERROR", 503)
    except ValueError:
        return error_response("The AI provider returned an unusable transaction draft. Try again or enter the transaction manually.", "AI_PROVIDER_INVALID_RESPONSE", 502)
    return jsonify(data=result)


@api_v2.get("/transactions")
@jwt_required()
def list_transactions_v2():
    try:
        page = _query_integer("page", 1)
        page_size = _query_integer("page_size", 25)
        response_body = list_transactions(
            int(get_jwt_identity()), request.args.get("scope", "current_month"), page, page_size
        )
    except ValueError as error:
        return error_response(str(error), "VALIDATION_ERROR", 400, getattr(error, "fields", None))
    return jsonify(response_body)


@api_v2.get("/transactions/<int:transaction_id>")
@jwt_required()
def get_transaction_v2(transaction_id: int):
    try:
        transaction = get_transaction(transaction_id, int(get_jwt_identity()))
    except TransactionNotFoundError as error:
        return error_response(str(error), "NOT_FOUND", 404)
    except TransactionForbiddenError as error:
        return error_response(str(error), "FORBIDDEN", 403)
    return jsonify(data=serialize_created_transaction(transaction))


@api_v2.put("/transactions/<int:transaction_id>")
@jwt_required()
def update_transaction_v2(transaction_id: int):
    try:
        response_body, status_code = update_transaction(
            transaction_id, int(get_jwt_identity()), request.get_json(silent=True),
            request.headers.get("Idempotency-Key"),
        )
    except TransactionNotFoundError as error:
        return error_response(str(error), "NOT_FOUND", 404)
    except TransactionForbiddenError as error:
        return error_response(str(error), "FORBIDDEN", 403)
    except StaleTransactionError as error:
        return error_response(str(error), "CONFLICT", 409)
    except ValueError as error:
        fields = getattr(error, "fields", None)
        code = "IDEMPOTENCY_KEY_REQUIRED" if "Idempotency-Key" in (fields or {}) else "VALIDATION_ERROR"
        return error_response(str(error), code, 400, fields)
    return jsonify(response_body), status_code


@api_v2.delete("/transactions/<int:transaction_id>")
@jwt_required()
def delete_transaction_v2(transaction_id: int):
    try:
        response_body, status_code = delete_transaction(
            transaction_id, int(get_jwt_identity()), request.headers.get("Idempotency-Key")
        )
    except TransactionNotFoundError as error:
        return error_response(str(error), "NOT_FOUND", 404)
    except TransactionForbiddenError as error:
        return error_response(str(error), "FORBIDDEN", 403)
    except ValueError as error:
        fields = getattr(error, "fields", None)
        code = "IDEMPOTENCY_KEY_REQUIRED" if "Idempotency-Key" in (fields or {}) else "VALIDATION_ERROR"
        return error_response(str(error), code, 400, fields)
    return jsonify(response_body), status_code


def _query_integer(name: str, default: int) -> int:
    value = request.args.get(name)
    if value is None:
        return default
    try:
        if not value.isdecimal():
            raise ValueError
        return int(value)
    except ValueError:
        from ..services.validators import ValidationError
        raise ValidationError(f"{name} must be a positive integer.", {name: "Enter a positive integer."}) from None


@api_v2.get("/openapi.json")
def openapi_v2():
    return send_file(OPENAPI_PATH, mimetype="application/json")


swagger_ui = get_swaggerui_blueprint(
    "/api/v2/docs",
    "/api/v2/openapi.json",
    config={"app_name": "Expense Tracker V2 API"},
)
