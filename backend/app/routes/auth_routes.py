from flask import Blueprint, jsonify, request

from ..serializers import serialize_user
from ..services.auth_service import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    login_user,
    register_user,
)
from ..services.validators import ValidationError
from ..utils import error_response


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    try:
        body = _get_json_body()
        result = register_user(body.get("email"), body.get("password"))
    except ValidationError as error:
        return error_response(str(error), "VALIDATION_ERROR", 400)
    except EmailAlreadyExistsError as error:
        return error_response(str(error), "EMAIL_ALREADY_EXISTS", 409)

    return (
        jsonify(
            message="User registered successfully.",
            data={"user": serialize_user(result.user)},
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    try:
        body = _get_json_body()
        result = login_user(body.get("email"), body.get("password"))
    except ValidationError as error:
        return error_response(str(error), "VALIDATION_ERROR", 400)
    except InvalidCredentialsError as error:
        return error_response(str(error), "INVALID_CREDENTIALS", 401)

    return jsonify(
        message="Login successful.",
        data={
            "access_token": result.access_token,
            "user": serialize_user(result.user),
        },
    )


def _get_json_body() -> dict[str, object]:
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ValidationError("Request body must be a valid JSON object.")
    return body
