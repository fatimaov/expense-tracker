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
from ..services.assisted_entry_service import (
    MAX_RECEIPT_BYTES,
    ReceiptUploadValidationError,
    create_receipt_transaction_draft,
    create_text_transaction_draft,
    validate_receipt_image,
)
from ..services.ai_request_guard import record_provider_request_start
from ..services.companion_service import (
    COMPANION_RESPONSE_SCHEMA,
    COMPANION_SYSTEM_INSTRUCTIONS,
    build_companion_fallback_response,
    build_companion_evidence,
    validate_companion_response,
)
from ..services.transaction_evidence_service import TransactionEvidenceService
from ..services.companion_proposal_service import (
    PROPOSAL_RESPONSE_SCHEMA,
    PROPOSAL_SYSTEM_INSTRUCTIONS,
    StaleProposalVersion,
    TargetTransactionUnavailable,
    build_explicit_action_proposal,
    build_reviewed_proposal,
    build_target_evidence,
    validate_proposal_response,
)
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


@api_v2.post("/companion/query")
@jwt_required()
def query_companion_v2():
    payload = request.get_json(silent=True)
    allowed_shapes = (
        {"question", "scope"},
        {"question", "scope", "target_transaction_id"},
        {"question", "scope", "target_transaction_id", "proposal_review"},
    )
    if not isinstance(payload, dict) or set(payload) not in allowed_shapes:
        return error_response("Provide a question and scope.", "VALIDATION_ERROR", 400, {
            "question": "Enter a question of 1 to 1,000 characters.",
            "scope": "Choose current_month or all.",
        })
    question = payload["question"]
    scope = payload["scope"]
    target_id = payload.get("target_transaction_id")
    proposal_review = payload.get("proposal_review")
    fields = {}
    if not isinstance(question, str) or not question.strip() or len(question) > 1000:
        fields["question"] = "Enter a question of 1 to 1,000 characters."
    if not isinstance(scope, str) or scope not in {"current_month", "all"}:
        fields["scope"] = "Choose current_month or all."
    if "target_transaction_id" in payload and (type(target_id) is not int or target_id <= 0):
        fields["target_transaction_id"] = "Select one transaction from the matching records."
    if fields:
        return error_response("The Companion request is invalid.", "VALIDATION_ERROR", 400, fields)

    user_id = int(get_jwt_identity())
    target_mode = target_id is not None
    intent = None
    try:
        if target_mode:
            try:
                target, evidence = build_target_evidence(user_id, scope, target_id, TransactionEvidenceService())
            except TargetTransactionUnavailable:
                base = TransactionEvidenceService().build(user_id, scope)
                evidence = {key: base[key] for key in ("scope", "timezone", "period", "exclusions", "warnings")}
                clarification = "Select one current transaction within the chosen scope and ask again."
                return jsonify(data={
                    "kind": "clarification", "message": clarification,
                    "missing_or_ambiguous_information": clarification,
                    "scope": scope, "period": evidence["period"], "evidence": evidence,
                })
            if "proposal_review" in payload:
                try:
                    result = build_reviewed_proposal(user_id, scope, target_id, proposal_review, TransactionEvidenceService())
                except StaleProposalVersion as error:
                    return error_response(str(error), "STALE_PROPOSAL_VERSION", 409)
                except ValueError as error:
                    return error_response(str(error), "VALIDATION_ERROR", 400)
                return jsonify(data={**result, "scope": scope, "period": evidence["period"]})
            try:
                result = build_explicit_action_proposal(question, target, evidence)
            except ValueError as error:
                return error_response(
                    str(error), "VALIDATION_ERROR", 400, getattr(error, "fields", None),
                )
            if result is not None:
                return jsonify(data={**result, "scope": scope, "period": evidence["period"]})
        else:
            intent, clarification, evidence = build_companion_evidence(
                user_id, scope, question, TransactionEvidenceService()
            )
        if not target_mode and intent is None:
            return jsonify(data={
                "kind": "clarification",
                "message": clarification,
                "missing_or_ambiguous_information": clarification,
                "scope": scope,
                "period": evidence["period"],
                "evidence": evidence,
            })
        settings = AISettings.from_mapping(current_app.config)
        generator = create_json_generator(settings)
        record_provider_request_start(int(get_jwt_identity()))
        response = generator.generate_json(
            PROPOSAL_SYSTEM_INSTRUCTIONS if target_mode else COMPANION_SYSTEM_INSTRUCTIONS,
            question,
            evidence,
            PROPOSAL_RESPONSE_SCHEMA if target_mode else COMPANION_RESPONSE_SCHEMA,
        )
        try:
            result = validate_proposal_response(response, target, evidence) if target_mode else validate_companion_response(response, evidence)
        except ValueError as error:
            current_app.logger.warning("Companion provider response failed validation: %s", error)
            if target_mode:
                message = "I couldn't prepare a safe change proposal. Review the selected record and ask again with one supported change."
                result = {
                    "kind": "clarification", "message": message,
                    "missing_or_ambiguous_information": message, "evidence": evidence,
                }
            else:
                result = build_companion_fallback_response(intent, evidence)
    except AIRateLimitExceededError as error:
        return error_response(str(error), "RATE_LIMIT_EXCEEDED", 429)
    except AIProviderTimeoutError as error:
        return error_response(str(error), "AI_PROVIDER_TIMEOUT", 504)
    except AIProviderResponseError as error:
        current_app.logger.warning("Companion provider returned an unusable response: %s", error)
        if target_mode:
            message = "I couldn't prepare a safe change proposal because the provider returned an unusable response. Try again or use Transaction History."
            return jsonify(data={
                "kind": "clarification", "message": message,
                "missing_or_ambiguous_information": message,
                "scope": scope, "period": evidence["period"], "evidence": evidence,
            })
        fallback = build_companion_fallback_response(intent, evidence)
        return jsonify(data={**fallback, "scope": scope, "period": evidence["period"]})
    except AIProviderUnavailableError as error:
        return error_response(str(error), "AI_PROVIDER_UNAVAILABLE", 503)
    except AIConfigurationError as error:
        return error_response(str(error), "AI_CONFIGURATION_ERROR", 503)
    except AIUnsupportedSchemaError as error:
        return error_response(str(error), "AI_CONFIGURATION_ERROR", 503)
    return jsonify(data={**result, "scope": scope, "period": evidence["period"]})


@api_v2.post("/assisted-entry/receipt")
@jwt_required()
def create_receipt_draft_v2():
    if request.mimetype != "multipart/form-data":
        return error_response(
            "Upload one receipt image as multipart form data.",
            "VALIDATION_ERROR",
            400,
            {"receipt": "Choose one JPEG, PNG, or WebP image."},
        )
    # Leave room for multipart headers while enforcing the image-size limit on its bytes below.
    if request.content_length is not None and request.content_length > MAX_RECEIPT_BYTES + 65536:
        return error_response(
            "The receipt image is larger than 10 MB.", "UPLOAD_TOO_LARGE", 413,
            {"receipt": "Choose an image that is 10 MB or smaller."},
        )

    uploaded_files = [
        (field, file)
        for field in request.files
        for file in request.files.getlist(field)
    ]
    if len(uploaded_files) != 1 or uploaded_files[0][0] != "receipt":
        return error_response(
            "Upload exactly one receipt image.", "VALIDATION_ERROR",
            400, {"receipt": "Choose exactly one image file."},
        )
    if request.form:
        return error_response(
            "Upload only the receipt image.", "VALIDATION_ERROR",
            400, {"receipt": "Remove additional form fields and try again."},
        )
    receipt_file = uploaded_files[0][1]
    if not receipt_file.filename:
        return error_response(
            "Choose a receipt image.", "VALIDATION_ERROR",
            400, {"receipt": "Choose a file before creating a draft."},
        )
    media_type = (receipt_file.mimetype or "").split(";", 1)[0].lower()
    if media_type not in {"image/jpeg", "image/png", "image/webp"}:
        return error_response(
            "Choose a JPEG, PNG, or WebP image.", "VALIDATION_ERROR",
            400, {"receipt": "This image format is not supported."},
        )
    image_bytes = receipt_file.stream.read(MAX_RECEIPT_BYTES + 1)
    if len(image_bytes) > MAX_RECEIPT_BYTES:
        return error_response(
            "The receipt image is larger than 10 MB.", "UPLOAD_TOO_LARGE", 413,
            {"receipt": "Choose an image that is 10 MB or smaller."},
        )
    try:
        validate_receipt_image(image_bytes, media_type)
    except ReceiptUploadValidationError as error:
        return error_response(str(error), "VALIDATION_ERROR", error.status_code, error.fields)

    try:
        settings = AISettings.from_mapping(current_app.config)
        generator = create_json_generator(settings)
        record_provider_request_start(int(get_jwt_identity()))
        result = create_receipt_transaction_draft(image_bytes, media_type, generator)
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
        return error_response(
            "The AI provider returned an unusable receipt draft. Try again or enter the transaction manually.",
            "AI_PROVIDER_INVALID_RESPONSE", 502,
        )
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
