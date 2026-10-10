from datetime import date, datetime, timedelta
from decimal import Decimal
import re
from io import BytesIO
import warnings
from zoneinfo import ZoneInfo

from sqlalchemy import select
from PIL import Image

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

RECEIPT_DRAFT_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["transaction_type", "amount", "transaction_date", "category_key", "notes", "uncertainties"],
    "properties": {
        "transaction_type": {"anyOf": [{"type": "string", "enum": ["expense"]}, {"type": "null"}]},
        "amount": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "transaction_date": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "category_key": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "notes": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "uncertainties": TEXT_DRAFT_RESPONSE_SCHEMA["properties"]["uncertainties"],
    },
}

RECEIPT_MEDIA_FORMATS = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}
MAX_RECEIPT_BYTES = 10 * 1024 * 1024

RECEIPT_SYSTEM_INSTRUCTIONS = (
    "Extract a draft for one expense from this receipt. Use only the supplied fixed expense categories and current date. "
    "Return transaction_type as expense or null. Never propose income, B/U/C, or reflective context. "
    "Extract only a clearly printed final payable total, transaction date, supported expense category, and concise merchant "
    "or relevant receipt detail for notes. Do not invent or estimate a total, date, merchant, category, or tax treatment. "
    "Return the final payable total in amount as a plain decimal string using a dot as the decimal separator, "
    "without currency symbols or thousands separators (for example, a printed 1.234,56 € becomes \"1234.56\"). "
    "Do not return the amount as a JSON number. "
    "This is a Spanish receipt: interpret printed dates as day/month/year, not month/day/year. "
    "Return transaction_date as YYYY-MM-DD; for example, 02/08/24 means 2024-08-02. "
    "Use the transaction date printed on the receipt, not today's date or a ticket/control number. "
    "If a value is missing, uncertain, or unreadable, return null and briefly explain it in uncertainties. "
    "Return only the requested JSON object."
)


class ReceiptUploadValidationError(ValueError):
    def __init__(self, message: str, fields: dict[str, str], status_code: int = 400):
        super().__init__(message)
        self.fields = fields
        self.status_code = status_code


def validate_receipt_image(image_bytes: bytes, media_type: str) -> None:
    expected_format = RECEIPT_MEDIA_FORMATS.get(media_type)
    if expected_format is None:
        raise ReceiptUploadValidationError(
            "Choose a JPEG, PNG, or WebP image.", {"receipt": "This image format is not supported."}
        )
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_bytes), formats=[expected_format]) as image:
                if image.format != expected_format:
                    raise ValueError("Image format does not match its media type.")
                image.verify()
            with Image.open(BytesIO(image_bytes), formats=[expected_format]) as image:
                if image.format != expected_format:
                    raise ValueError("Image format does not match its media type.")
                image.load()
    except Exception as error:
        raise ReceiptUploadValidationError(
            "The uploaded image could not be read. Choose a valid JPEG, PNG, or WebP image.",
            {"receipt": "This image is invalid or damaged."},
        ) from error


def create_receipt_transaction_draft(
    image_bytes: bytes, media_type: str, generator, now: datetime | None = None
) -> dict:
    """Return a validated, transient receipt draft without writing transaction data."""
    categories = list(db.session.scalars(
        select(Category).where(Category.transaction_type == "expense").order_by(Category.key)
    ).all())
    current = now or datetime.now(APP_TIMEZONE)
    current_date = current.astimezone(APP_TIMEZONE).date() if current.tzinfo else current.date()
    context = {
        "media_type": media_type,
        "current_date": current_date.isoformat(),
        "categories": [
            {"key": category.key, "label": category.label, "transaction_type": category.transaction_type}
            for category in categories
        ],
    }
    proposed = generator.generate_json_from_image(
        RECEIPT_SYSTEM_INSTRUCTIONS,
        image_bytes,
        media_type,
        context,
        RECEIPT_DRAFT_RESPONSE_SCHEMA,
    )
    proposed = _normalize_receipt_draft(proposed)
    return _validate_provider_draft(proposed, categories, current_date, allowed_types={"expense"})


_RECEIPT_AMOUNT_CURRENCY = re.compile(r"(?:€|\$|£|EUR|USD|GBP)", re.IGNORECASE)


def _normalize_receipt_draft(proposed: object) -> object:
    """Normalize common receipt amount and Spanish date formats before validation."""
    if not isinstance(proposed, dict):
        return proposed

    corrected = dict(proposed)
    amount = proposed.get("amount")
    if isinstance(amount, (int, float, Decimal)) and not isinstance(amount, bool):
        amount = str(amount)
    if isinstance(amount, str):
        cleaned = _RECEIPT_AMOUNT_CURRENCY.sub("", amount).strip()
        cleaned = cleaned.replace("\u00a0", "").replace(" ", "")
        if re.fullmatch(r"[+-]?[0-9][0-9.,]*", cleaned):
            sign = ""
            if cleaned[:1] in {"+", "-"}:
                sign, cleaned = cleaned[0], cleaned[1:]
            if cleaned and cleaned[-1].isdigit():
                if "." in cleaned and "," in cleaned:
                    decimal_separator = "." if cleaned.rfind(".") > cleaned.rfind(",") else ","
                    grouping_separator = "," if decimal_separator == "." else "."
                    whole, fraction = cleaned.rsplit(decimal_separator, 1)
                    whole = whole.replace(grouping_separator, "")
                elif "," in cleaned or "." in cleaned:
                    separator = "," if "," in cleaned else "."
                    pieces = cleaned.split(separator)
                    if len(pieces) > 2:
                        if all(len(piece) == 3 for piece in pieces[1:]):
                            whole, fraction = "".join(pieces), ""
                        else:
                            whole, fraction = "", "invalid"
                    elif len(pieces[1]) == 3:
                        whole, fraction = "".join(pieces), ""
                    else:
                        whole, fraction = pieces
                else:
                    whole, fraction = cleaned, ""
                if whole.isdigit() and (not fraction or fraction.isdigit()) and len(fraction) <= 2:
                    corrected["amount"] = f"{sign}{whole}.{fraction.ljust(2, '0')}" if fraction else f"{sign}{whole}.00"

    transaction_date = proposed.get("transaction_date")
    if isinstance(transaction_date, str):
        match = re.fullmatch(r"\s*(\d{1,2})[./-](\d{1,2})[./-](\d{2}|\d{4})\s*", transaction_date)
        if match:
            day, month, year = (int(part) for part in match.groups())
            if year < 100:
                year += 2000 if year <= 69 else 1900
            try:
                corrected["transaction_date"] = date(year, month, day).isoformat()
            except ValueError:
                pass
    return corrected

SYSTEM_INSTRUCTIONS = (
    "Extract a draft for one one-time income or expense from the user's text. "
    "Use only the supplied fixed categories and current date. Never infer B/U/C or reflective context. "
    "If the text states an amount, copy its numeric value into amount as a decimal string without a currency symbol "
    "(for example, 12.50 euros becomes \"12.50\"); never return an empty string for amount. "
    "Use null only when the amount is genuinely absent or unclear. Resolve relative dates such as yesterday "
    "from current_date in the supplied evidence and return transaction_date as YYYY-MM-DD. "
    "Use a matching supplied category key and do not mark a supplied valid key as uncertain. "
    "Set unclear fields to null and explain uncertainty briefly. Return only the requested JSON object."
)

_RELATIVE_DATE_PATTERN = re.compile(
    r"\bday before yesterday\b|\byesterday\b|\btoday\b|\blast\s+"
    r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.IGNORECASE,
)
_WEEKDAY_NUMBERS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _resolve_relative_transaction_date(text: str, current_date: date) -> date | None:
    match = _RELATIVE_DATE_PATTERN.search(text)
    if match is None:
        return None

    phrase = match.group(0).casefold()
    if phrase == "today":
        return current_date
    if phrase == "yesterday":
        return current_date - timedelta(days=1)
    if phrase == "day before yesterday":
        return current_date - timedelta(days=2)

    weekday = phrase.split()[-1]
    days_back = (current_date.weekday() - _WEEKDAY_NUMBERS[weekday]) % 7 or 7
    return current_date - timedelta(days=days_back)


def _apply_deterministic_transaction_date(text: str, proposed: object, current_date: date) -> object:
    resolved_date = _resolve_relative_transaction_date(text, current_date)
    if resolved_date is None or not isinstance(proposed, dict) or "transaction_date" not in proposed:
        return proposed

    corrected = dict(proposed)
    corrected["transaction_date"] = resolved_date.isoformat()
    uncertainties = corrected.get("uncertainties")
    if isinstance(uncertainties, list):
        corrected["uncertainties"] = [
            item for item in uncertainties
            if not isinstance(item, dict) or item.get("field") != "transaction_date"
        ]
    return corrected


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
    proposed = _apply_deterministic_transaction_date(text, proposed, current_date)
    return _validate_provider_draft(proposed, categories, current_date)


def _validate_provider_draft(
    proposed: object,
    categories: list[Category],
    current_date: date,
    allowed_types: set[str] = {"income", "expense"},
) -> dict:
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
            if value not in allowed_types:
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
