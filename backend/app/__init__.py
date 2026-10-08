from flask import Flask

from .admin import init_admin
from . import models
from .config import Config
from .extensions import cors, db, jwt, migrate
from .routes import blueprints


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    if app.config["ENABLE_ADMIN"] and app.config["FLASK_ENV"] == "development":
        init_admin(app)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    app.add_url_rule(
        "/api/v2/docs",
        endpoint="swagger_ui.docs_without_trailing_slash",
        view_func=app.view_functions["swagger_ui.show"],
        defaults={"path": None},
    )

    return app
