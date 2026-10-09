from app.config import _sqlalchemy_database_uri
from sqlalchemy.engine import make_url


def test_generic_postgresql_url_uses_installed_psycopg2_driver():
    uri = _sqlalchemy_database_uri("postgresql://user:password@localhost:5432/expenses")
    assert make_url(uri).drivername == "postgresql+psycopg2"


def test_explicit_postgresql_driver_is_preserved():
    uri = _sqlalchemy_database_uri("postgresql+psycopg2://user:password@localhost:5432/expenses")
    assert make_url(uri).drivername == "postgresql+psycopg2"
