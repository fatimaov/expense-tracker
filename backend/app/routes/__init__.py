from flask import Blueprint

from .auth_routes import auth_bp
from .category_routes import category_bp
from .expense_routes import expense_bp
from .user_routes import user_bp


api = Blueprint("api", __name__, url_prefix="/api")


from . import health  # noqa: E402, F401


blueprints = (api, auth_bp, category_bp, expense_bp, user_bp)

__all__ = ["blueprints"]
