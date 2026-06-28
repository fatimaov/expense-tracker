from flask import Flask

from . import models
from .config import Config
from .extensions import cors, db, jwt, migrate
from .routes import api
from .routes.auth_routes import auth_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(api)
    app.register_blueprint(auth_bp)

    return app
