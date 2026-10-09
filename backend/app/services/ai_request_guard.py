from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from ..ai.errors import AIRateLimitExceededError, AIConfigurationError
from ..extensions import db
from ..models import AIRequestAttempt, User


MAX_REQUESTS = 10
WINDOW = timedelta(minutes=15)


def record_provider_request_start(user_id: int, now: datetime | None = None) -> None:
    """Atomically reserve one of the user's 10 starts in the rolling window."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    cutoff = current - WINDOW
    try:
        # PostgreSQL row locking serializes checks for the same user while allowing
        # unrelated users to proceed independently.
        user = db.session.scalar(select(User.id).where(User.id == user_id).with_for_update())
        if user is None:
            db.session.rollback()
            raise AIConfigurationError("The authenticated user is unavailable.")
        db.session.execute(delete(AIRequestAttempt).where(
            AIRequestAttempt.user_id == user_id,
            AIRequestAttempt.started_at <= cutoff,
        ))
        count = db.session.scalar(select(func.count(AIRequestAttempt.id)).where(
            AIRequestAttempt.user_id == user_id,
            AIRequestAttempt.started_at > cutoff,
            AIRequestAttempt.started_at <= current,
        )) or 0
        if count >= MAX_REQUESTS:
            db.session.rollback()
            raise AIRateLimitExceededError("AI request limit reached. Try again after the current window expires.")
        db.session.add(AIRequestAttempt(user_id=user_id, started_at=current))
        db.session.commit()
    except (AIRateLimitExceededError, AIConfigurationError):
        raise
    except Exception as error:
        db.session.rollback()
        raise AIConfigurationError("The AI request limit could not be checked safely.") from error
