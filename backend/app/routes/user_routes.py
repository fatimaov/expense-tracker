from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import User
from ..services.auth_service import get_user_by_id


user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.get("/me")
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(error="User not found."), 404

    user = get_user_by_id(user_id)
    if user is None:
        return jsonify(error="User not found."), 404

    return jsonify(
        message="User retrieved successfully.",
        data={"user": _user_data(user)},
    )


def _user_data(user: User) -> dict[str, int | str]:
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }
