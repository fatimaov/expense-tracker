from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select

from ..extensions import db
from ..models import Category
from .transaction_service import TRANSACTION_AMOUNT_PATTERN, TRANSACTION_DATE_PATTERN


APP_TIMEZONE = ZoneInfo("Europe/Madrid")
ALLOWED_DRAFT_FIELDS = {"transaction_type", "amount", "transaction_date", "category_key", "notes"}
REQUIRED_DRAFT_FIELDS = ("transaction_type", "amount", "transaction_date", "category_key")

TEXT_DRAFT_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["transaction_type", "amount", "transaction_date", "category_key", "notes", "uncertainties"],
    "properties": {
        "transaction_type": {"anyOf": [{"type": "string", "enum": ["income", "expense"]}, {"type": "null"}]},
        "amount": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "transaction_date": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "category_key": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "notes": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "uncertainties": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["field", "reason"],
                "properties": {
                    "field": {"type": "string", "enum": sorted(ALLOWED_DRAFT_FIELDS)},
                    "reason": {"type": "string"},
                },
            },
        },
    },
}

SYSTEM_INSTRUCTIONS = (
    "Extract a draft for one one-time income or expense from the user's text. "
    "Use only the supplied fixed categories and current date. Never infer B/U/C or reflective context. "
    "Set unclear fields to null and explain uncertainty briefly. Return only the requested JSON object."
)


def create_text_transaction_draft(text: str, generator, now: datetime | None = None) -> dict:
    """Return a validated, transient transaction draft without writing transaction data."""
    categories = list(db.session.scalars(
        select(Category).order_by(Category.transaction_type, Category.key)
    ).all())
    current = now or datetime.now(APP_TIMEZONE)
    current_date = current.astimezone(APP_TIMEZONE).date() if current.tzinfo else current.date()
    context = {
        "current_date": current_date.isoformat(),
        "categories": [
            {"key": category.key, "label": category.label, "transaction_type": category.transaction_type}
            for category in categories
        ],
    }
    proposed = generator.generate_json(
        SYSTEM_INSTRUCTIONS,
        text,
        context,
        TEXT_DRAFT_RESPONSE_SCHEMA,
    )
    return _validate_provider_draft(proposed, categories, current_date)


def _validate_provider_draft(proposed: object, categories: list[Category], current_date: date) -> dict:
    if not isinstance(proposed, dict) or set(proposed) != set(TEXT_DRAFT_RESPONSE_SCHEMA["required"]):
        raise ValueError("The AI provider returned an unusable transaction draft.")

    by_key = {category.key: category for category in categories}
    raw = {field: proposed[field] for field in ALLOWED_DRAFT_FIELDS}
    uncertain = {}
    raw_uncertainties = proposed["uncertainties"]
    if not isinstance(raw_uncertainties, list):
        raise ValueError("The AI provider returned an unusable transaction draft.")
    for item in raw_uncertainties:
        if not isinstance(item, dict) or set(item) != {"field", "reason"}:
            raise ValueError("The AI provider returned an unusable transaction draft.")
        field, reason = item["field"], item["reason"]
        if not isinstance(field, str) or field not in ALLOWED_DRAFT_FIELDS or not isinstance(reason, str) or not reason.strip():
            raise ValueError("The AI provider returned an unusable transaction draft.")
        uncertain[field] = reason.strip()[:240]

    draft = {field: None for field in ALLOWED_DRAFT_FIELDS}
    for field, value in raw.items():
        if value is None:
            continue
        if not isinstance(value, str):
            uncertain.setdefault(field, "The suggested value could not be validated.")
            continue
        if field == "transaction_type":
            if value not in {"income", "expense"}:
                uncertain.setdefault(field, "Choose income or expense before saving.")
                continue
        elif field == "amount":
            if not TRANSACTION_AMOUNT_PATTERN.fullmatch(value) or Decimal(value) <= 0:
                uncertain.setdefault(field, "Check the amount before saving.")
                continue
        elif field == "transaction_date":
            if not TRANSACTION_DATE_PATTERN.fullmatch(value):
                uncertain.setdefault(field, "Check the date before saving.")
                continue
            try:
                parsed_date = date.fromisoformat(value)
            except ValueError:
                uncertain.setdefault(field, "Check the date before saving.")
                continue
            if parsed_date > current_date:
                uncertain.setdefault(field, "The date is in the future; choose today or an earlier date.")
                continue
        elif field == "category_key":
            category = by_key.get(value)
            if category is None or raw["transaction_type"] not in {"income", "expense"} or category.transaction_type != raw["transaction_type"]:
                uncertain.setdefault(field, "Choose a supported category for this transaction type.")
                continue
        elif field == "notes":
            if len(value) > 1000:
                uncertain.setdefault(field, "Shorten the notes before saving.")
                continue
            value = value.strip() or None
        draft[field] = value

    for field in uncertain:
        draft[field] = None
    missing_fields = [field for field in REQUIRED_DRAFT_FIELDS if draft[field] is None]
    uncertainties = [{"field": field, "reason": reason} for field, reason in uncertain.items()]
    return {"draft": draft, "missing_fields": missing_fields, "uncertainties": uncertainties}
