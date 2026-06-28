import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)


def _as_bool(value: str | None) -> bool:
    return value is not None and value.lower() in {"1", "true", "yes", "on"}


def _as_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = _as_bool(os.getenv("FLASK_DEBUG"))
    DEBUG = FLASK_DEBUG
    CORS_ORIGINS = _as_list(
        os.getenv("CORS_ORIGINS", "http://localhost:5173")
    )
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    CORS_RESOURCES = {r"/api/*": {"origins": CORS_ORIGINS}}
