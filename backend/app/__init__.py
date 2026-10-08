from flask import Flask

from .admin import init_admin
from . import models
from .config import Config
from .extensions import cors, db, jwt, migrate
from .routes import blueprints


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    init_admin(app)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app
