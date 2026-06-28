from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()


@jwt.unauthorized_loader
def handle_missing_token(_reason: str):
    return jsonify(error="Authorization token is required."), 401


@jwt.invalid_token_loader
def handle_invalid_token(_reason: str):
    return jsonify(error="Authorization token is invalid."), 401


@jwt.expired_token_loader
def handle_expired_token(_jwt_header: dict, _jwt_payload: dict):
    return jsonify(error="Authorization token has expired."), 401
