from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..serializers import serialize_user
from ..services.auth_service import get_user_by_id
from ..utils import error_response


user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.get("/me")
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return error_response(
            "Authorization token identity is invalid.",
            "INVALID_TOKEN_IDENTITY",
            401,
        )

    user = get_user_by_id(user_id)
    if user is None:
        return error_response("User not found.", "USER_NOT_FOUND", 404)

    return jsonify(
        message="User retrieved successfully.",
        data={"user": serialize_user(user)},
    )
