from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme

from ..extensions import db
from ..models import Expense, User


class UserAdminView(ModelView):
    column_list = ("id", "email", "created_at")
    form_excluded_columns = ("password_hash", "expenses")


class ExpenseAdminView(ModelView):
    column_list = (
        "id",
        "user_id",
        "amount",
        "title",
        "expense_date",
        "category",
        "created_at",
    )
    form_excluded_columns = ("created_at", "user")


def init_admin(app: Flask) -> Admin:
    admin = Admin(
        name=app.config["ADMIN_NAME"],
        url=app.config["ADMIN_URL"],
        theme=Bootstrap4Theme(swatch=app.config["ADMIN_THEME_SWATCH"]),
    )
    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(ExpenseAdminView(Expense, db.session))
    admin.init_app(app)
    return admin
