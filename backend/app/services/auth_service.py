from dataclasses import dataclass

from flask_jwt_extended import create_access_token
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import User
from .validators import validate_email, validate_password


class AuthenticationError(ValueError):
    """Base exception for expected authentication service failures."""


class EmailAlreadyExistsError(AuthenticationError):
    """Raised when registration uses an email that is already registered."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials do not match a user."""


@dataclass(frozen=True, slots=True)
class AuthResult:
    user: User
    access_token: str | None = None


def register_user(email: object, password: object) -> AuthResult:
    validated_email = validate_email(email)
    validated_password = validate_password(password)

    existing_user = db.session.scalar(
        select(User).where(User.email == validated_email)
    )
    if existing_user is not None:
        raise EmailAlreadyExistsError("A user with this email already exists.")

    user = User(
        email=validated_email,
        password_hash=generate_password_hash(validated_password),
    )
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise EmailAlreadyExistsError(
            "A user with this email already exists."
        ) from None

    return AuthResult(user=user)


def login_user(email: object, password: object) -> AuthResult:
    validated_email = validate_email(email)
    validated_password = validate_password(password)

    user = db.session.scalar(select(User).where(User.email == validated_email))
    if user is None or not check_password_hash(
        user.password_hash,
        validated_password,
    ):
        raise InvalidCredentialsError("Invalid email or password.")

    access_token = create_access_token(identity=str(user.id))
    return AuthResult(user=user, access_token=access_token)


def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)
