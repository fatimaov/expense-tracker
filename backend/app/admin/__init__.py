from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme

from ..extensions import db
from ..models import Category, Transaction, User


class UserAdminView(ModelView):
    column_list = ("id", "email", "created_at")
    form_excluded_columns = ("password_hash", "transactions")


class ExpenseAdminView(ModelView):
    column_list = (
        "id",
        "user_id",
        "amount",
        "transaction_type",
        "transaction_date",
        "category",
        "created_at",
    )
    form_excluded_columns = ("created_at", "updated_at", "deleted_at", "user")


class CategoryAdminView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False


def init_admin(app: Flask) -> Admin:
    admin = Admin(
        name=app.config["ADMIN_NAME"],
        url=app.config["ADMIN_URL"],
        theme=Bootstrap4Theme(swatch=app.config["ADMIN_THEME_SWATCH"]),
    )
    admin.add_view(UserAdminView(User, db))
    admin.add_view(ExpenseAdminView(Transaction, db))
    admin.add_view(CategoryAdminView(Category, db))
    admin.init_app(app)
    return admin
