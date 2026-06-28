from ..models import User


def serialize_user(user: User) -> dict[str, int | str]:
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }
