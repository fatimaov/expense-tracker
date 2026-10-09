import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..extensions import db
from ..models import Category, IdempotencyRecord, Transaction
from .validators import ValidationError, validate_expense_date, validate_positive_amount, validate_required_string


CATEGORY_SEEDS = (
    ("expense_transport", "Transport", "expense"),
    ("expense_accommodation", "Accommodation", "expense"),
    ("expense_food", "Food", "expense"),
    ("expense_activities", "Activities", "expense"),
    ("expense_other", "Other", "expense"),
    ("income_salary", "Salary", "income"),
    ("income_other", "Other", "income"),
)
LEGACY_CATEGORY_KEYS = {
    "Transport": "expense_transport",
    "Accommodation": "expense_accommodation",
    "Food": "expense_food",
    "Activities": "expense_activities",
    "Other": "expense_other",
}


class TransactionNotFoundError(LookupError):
    pass


class TransactionForbiddenError(PermissionError):
    pass


class StaleTransactionError(RuntimeError):
    pass


TRANSACTION_AMOUNT_PATTERN = re.compile(r"^(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,2})?$")
TRANSACTION_DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
IDEMPOTENCY_TTL = timedelta(hours=24)
APP_TIMEZONE = ZoneInfo("Europe/Madrid")


def list_categories(transaction_type: str | None = None) -> list[Category]:
    query = select(Category).order_by(Category.id)
    if transaction_type:
        query = query.where(Category.transaction_type == transaction_type)
    return list(db.session.scalars(query).all())


def get_category(key_or_label: object, transaction_type: str = "expense") -> Category:
    key = LEGACY_CATEGORY_KEYS.get(key_or_label, key_or_label)
    category = db.session.scalar(select(Category).where(
        Category.key == key,
        Category.transaction_type == transaction_type,
    ))
    if category is None:
        raise ValidationError("Category is invalid for this transaction type.")
    return category


def create_expense(user_id: int, amount: object, title: object, expense_date: object, category: object, notes: object = None) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        transaction_type="expense",
        amount=validate_positive_amount(amount),
        transaction_date=validate_expense_date(expense_date),
        category=get_category(category),
        notes=combine_title_and_notes(title, notes),
    )
    db.session.add(transaction)
    _commit()
    return transaction


def create_transaction(user_id: int, payload: object, idempotency_key: object) -> tuple[dict, int]:
    """Validate and atomically create a V2 transaction with a replayable result."""
    key = _validate_idempotency_key(idempotency_key)
    existing = db.session.scalar(select(IdempotencyRecord).where(
        IdempotencyRecord.user_id == user_id,
        IdempotencyRecord.key == key,
    ))
    if existing is not None:
        created_at = existing.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - created_at < IDEMPOTENCY_TTL:
            return existing.response_body, existing.response_status
        db.session.delete(existing)
        db.session.flush()

    body = _validate_transaction_payload(payload)

    transaction = Transaction(
        user_id=user_id,
        transaction_type=body["transaction_type"],
        amount=body["amount"],
        transaction_date=body["transaction_date"],
        category=body["category"],
        notes=body["notes"],
    )
    db.session.add(transaction)
    try:
        db.session.flush()
        month = transaction.transaction_date.strftime("%Y-%m")
        response_body = {
            "data": serialize_created_transaction(transaction),
            "meta": {"affected_period_range": {"from": month, "to": month}},
        }
        db.session.add(IdempotencyRecord(
            user_id=user_id,
            key=key,
            response_status=201,
            response_body=response_body,
        ))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        replay = db.session.scalar(select(IdempotencyRecord).where(
            IdempotencyRecord.user_id == user_id,
            IdempotencyRecord.key == key,
        ))
        if replay is not None:
            created_at = replay.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - created_at < IDEMPOTENCY_TTL:
                return replay.response_body, replay.response_status
        raise
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return response_body, 201


def serialize_created_transaction(transaction: Transaction) -> dict:
    return {
        "id": transaction.id,
        "transaction_type": transaction.transaction_type,
        "amount": str(transaction.amount),
        "transaction_date": transaction.transaction_date.isoformat(),
        "category_key": transaction.category.key,
        "category_label": transaction.category.label,
        "notes": transaction.notes,
        "created_at": transaction.created_at.isoformat(),
        "updated_at": transaction.updated_at.isoformat(),
    }


def get_transaction(transaction_id: int, user_id: int) -> Transaction:
    transaction = db.session.get(Transaction, transaction_id)
    if transaction is None or transaction.deleted_at is not None:
        raise TransactionNotFoundError("Transaction not found.")
    if transaction.user_id != user_id:
        raise TransactionForbiddenError("You do not have access to this transaction.")
    return transaction


def list_transactions(user_id: int, scope: str = "current_month", page: int = 1, page_size: int = 25) -> dict:
    if scope not in {"current_month", "all"}:
        raise ValidationError("Scope must be current_month or all.", {"scope": "Choose current_month or all."})
    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        raise ValidationError("Page must be a positive integer.", {"page": "Enter a positive integer."})
    if isinstance(page_size, bool) or not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ValidationError("Page size must be between 1 and 100.", {"page_size": "Choose a value from 1 to 100."})

    today = datetime.now(APP_TIMEZONE).date()
    first_day = today.replace(day=1)
    next_month = date(first_day.year + (first_day.month == 12), first_day.month % 12 + 1, 1)
    base = select(Transaction).where(Transaction.user_id == user_id, Transaction.deleted_at.is_(None))
    if scope == "current_month":
        base = base.where(Transaction.transaction_date >= first_day, Transaction.transaction_date < next_month)

    total_records = db.session.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.session.scalars(
        base.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .offset((page - 1) * page_size).limit(page_size)
    ).all()

    summary_query = select(
        Transaction.transaction_type,
        func.count(Transaction.id),
        func.coalesce(func.sum(Transaction.amount), 0),
    ).where(Transaction.user_id == user_id, Transaction.deleted_at.is_(None))
    if scope == "current_month":
        summary_query = summary_query.where(Transaction.transaction_date >= first_day, Transaction.transaction_date < next_month)
    totals = db.session.execute(summary_query.group_by(Transaction.transaction_type)).all()
    income = sum((amount for kind, _, amount in totals if kind == "income"), Decimal("0"))
    expense = sum((amount for kind, _, amount in totals if kind == "expense"), Decimal("0"))

    category_query = select(Category.key, Category.label, Category.transaction_type, func.sum(Transaction.amount)).join(
        Transaction, Transaction.category_id == Category.id
    ).where(Transaction.user_id == user_id, Transaction.deleted_at.is_(None))
    if scope == "current_month":
        category_query = category_query.where(Transaction.transaction_date >= first_day, Transaction.transaction_date < next_month)
    category_totals = db.session.execute(category_query.group_by(Category.key, Category.label, Category.transaction_type).order_by(Category.transaction_type, Category.label)).all()
    return {
        "data": [serialize_created_transaction(row) for row in rows],
        "meta": {
            "pagination": {"page": page, "page_size": page_size, "total_records": total_records, "total_pages": (total_records + page_size - 1) // page_size},
            "scope": scope,
            "summary": {
                "record_count": total_records,
                "total_income": str(income),
                "total_expense": str(expense),
                "category_totals": [
                    {"category_key": key, "category_label": label, "transaction_type": kind, "total": str(amount)}
                    for key, label, kind, amount in category_totals
                ],
            },
        },
    }


def update_transaction(transaction_id: int, user_id: int, payload: object, idempotency_key: object) -> tuple[dict, int]:
    key = _validate_idempotency_key(idempotency_key)
    replay = _get_idempotency_replay(user_id, key)
    if replay is not None:
        return replay
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a valid JSON object.")
    expected = {"amount", "transaction_date", "category_key", "notes", "updated_at"}
    fields = {name: "This field is required." for name in expected - payload.keys()}
    fields.update({name: "This field is not supported." for name in payload.keys() - expected})
    if fields:
        raise ValidationError("Request contains missing or unsupported fields.", fields)
    transaction = get_transaction(transaction_id, user_id)
    if not isinstance(payload["updated_at"], str) or _parse_timestamp(payload["updated_at"]) != _as_utc(transaction.updated_at):
        raise StaleTransactionError("This transaction changed elsewhere. Review the latest version and try again.")
    body = _validate_transaction_payload({
        "transaction_type": transaction.transaction_type,
        "amount": payload["amount"],
        "transaction_date": payload["transaction_date"],
        "category_key": payload["category_key"],
        "notes": payload["notes"],
    })
    old_month = transaction.transaction_date.strftime("%Y-%m")
    transaction.amount = body["amount"]
    transaction.transaction_date = body["transaction_date"]
    transaction.category = body["category"]
    transaction.notes = body["notes"]
    transaction.updated_at = datetime.now(timezone.utc)
    affected = sorted([old_month, transaction.transaction_date.strftime("%Y-%m")])
    response_body = {"data": serialize_created_transaction(transaction), "meta": {"affected_period_range": {"from": affected[0], "to": affected[-1]}}}
    return _save_idempotent_result(user_id, key, response_body, 200)


def delete_transaction(transaction_id: int, user_id: int, idempotency_key: object) -> tuple[dict, int]:
    key = _validate_idempotency_key(idempotency_key)
    replay = _get_idempotency_replay(user_id, key)
    if replay is not None:
        return replay
    transaction = get_transaction(transaction_id, user_id)
    month = transaction.transaction_date.strftime("%Y-%m")
    transaction.deleted_at = datetime.now(timezone.utc)
    transaction.updated_at = datetime.now(timezone.utc)
    response_body = {"data": {"id": transaction.id, "deleted": True}, "meta": {"affected_period_range": {"from": month, "to": month}}}
    return _save_idempotent_result(user_id, key, response_body, 200)


def _get_idempotency_replay(user_id: int, key: str) -> tuple[dict, int] | None:
    existing = db.session.scalar(select(IdempotencyRecord).where(IdempotencyRecord.user_id == user_id, IdempotencyRecord.key == key))
    if existing is None:
        return None
    created_at = existing.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - created_at < IDEMPOTENCY_TTL:
        return existing.response_body, existing.response_status
    db.session.delete(existing)
    db.session.flush()
    return None


def _save_idempotent_result(user_id: int, key: str, body: dict, status: int) -> tuple[dict, int]:
    db.session.add(IdempotencyRecord(user_id=user_id, key=key, response_status=status, response_body=body))
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        replay = _get_idempotency_replay(user_id, key)
        if replay is not None:
            return replay
        raise
    return body, status


def _parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return _as_utc(parsed)


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _validate_transaction_payload(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    allowed = {"transaction_type", "amount", "transaction_date", "category_key", "notes"}
    fields: dict[str, str] = {}
    for name in ("b_u_c", "reflective_context"):
        if name in payload:
            fields[name] = "This field is not supported by transaction creation."
    for name in set(payload) - allowed - {"b_u_c", "reflective_context"}:
        fields[name] = "This field is not supported."
    for name in ("transaction_type", "amount", "transaction_date", "category_key"):
        if name not in payload:
            fields[name] = "This field is required."
    if fields:
        raise ValidationError("Request contains missing or unsupported fields.", fields)

    transaction_type = payload["transaction_type"]
    if not isinstance(transaction_type, str) or transaction_type not in {"income", "expense"}:
        fields["transaction_type"] = "Select income or expense."

    amount_raw = payload["amount"]
    amount = None
    if not isinstance(amount_raw, str) or not TRANSACTION_AMOUNT_PATTERN.fullmatch(amount_raw):
        fields["amount"] = "Enter a positive amount with up to 12 digits and 2 decimal places."
    else:
        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                fields["amount"] = "Amount must be greater than zero."
        except InvalidOperation:
            fields["amount"] = "Enter a valid amount."

    transaction_date = None
    try:
        if not isinstance(payload["transaction_date"], str) or not TRANSACTION_DATE_PATTERN.fullmatch(payload["transaction_date"]):
            raise ValidationError("Transaction date must use YYYY-MM-DD format.")
        transaction_date = validate_expense_date(payload["transaction_date"])
        if transaction_date > datetime.now(APP_TIMEZONE).date():
            fields["transaction_date"] = "Transaction date cannot be in the future."
    except ValidationError as error:
        fields["transaction_date"] = str(error)

    category = None
    category_key = payload["category_key"]
    if not isinstance(category_key, str):
        fields["category_key"] = "Choose a valid category."
    elif isinstance(transaction_type, str) and transaction_type in {"income", "expense"}:
        try:
            category = get_category(category_key, transaction_type)
        except ValidationError as error:
            fields["category_key"] = str(error)

    notes = payload.get("notes", "")
    if notes is None or not isinstance(notes, str):
        fields["notes"] = "Notes must be a string."

    if fields:
        raise ValidationError("Transaction details are invalid.", fields)
    return {
        "transaction_type": transaction_type,
        "amount": amount,
        "transaction_date": transaction_date,
        "category": category,
        "notes": notes.strip() or None,
    }


def _validate_idempotency_key(value: object) -> str:
    try:
        parsed = UUID(value) if isinstance(value, str) else None
    except (ValueError, AttributeError):
        parsed = None
    if parsed is None or parsed.version != 4:
        raise ValidationError("Idempotency-Key must be a UUID v4.", {"Idempotency-Key": "Provide a UUID v4 key."})
    return str(parsed)


def get_user_expenses(user_id: int) -> list[Transaction]:
    statement = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.deleted_at.is_(None),
    ).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
    return list(db.session.scalars(statement).all())


def get_expense_by_id(expense_id: int, user_id: int) -> Transaction | None:
    return db.session.scalar(select(Transaction).where(
        Transaction.id == expense_id,
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.deleted_at.is_(None),
    ))


def update_expense(expense_id: int, user_id: int, amount: object, title: object, expense_date: object, category: object, notes: object = None) -> Transaction:
    transaction = _get_owned_expense(expense_id, user_id)
    transaction.amount = validate_positive_amount(amount)
    transaction.notes = combine_title_and_notes(title, notes)
    transaction.transaction_date = validate_expense_date(expense_date)
    transaction.category = get_category(category)
    _commit()
    return transaction


def delete_expense(expense_id: int, user_id: int) -> None:
    transaction = _get_owned_expense(expense_id, user_id)
    transaction.deleted_at = datetime.now(timezone.utc)
    _commit()


def legacy_title_and_notes(transaction: Transaction) -> tuple[str, str | None]:
    value = (transaction.notes or "").strip()
    title, separator, notes = value.partition("\n\n")
    return (title, notes.strip() or None) if separator else (value, None)


def combine_title_and_notes(title: object, notes: object) -> str | None:
    cleaned_title = validate_required_string(title, "Title").strip()
    if notes is None:
        cleaned_notes = ""
    elif isinstance(notes, str):
        cleaned_notes = notes.strip()
    else:
        raise ValidationError("Notes must be a string.")
    combined = f"{cleaned_title}\n\n{cleaned_notes}" if cleaned_notes else cleaned_title
    return combined.strip() or None


def _get_owned_expense(expense_id: int, user_id: int) -> Transaction:
    transaction = get_expense_by_id(expense_id, user_id)
    if transaction is None:
        raise TransactionNotFoundError("Expense not found.")
    return transaction


def _commit() -> None:
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
