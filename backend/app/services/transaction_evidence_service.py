from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select

from ..extensions import db
from ..models import Transaction


APP_TIMEZONE = ZoneInfo("Europe/Madrid")


class EvidenceSelectionError(ValueError):
    """A requested selected transaction is not available to the caller."""


class TransactionEvidenceService:
    """Build JSON-ready, deterministic evidence without exposing the session."""

    def __init__(self, now_provider=None):
        self._now_provider = now_provider or (lambda: datetime.now(APP_TIMEZONE))

    def build(self, user_id: int, scope: str = "current_month", selected_ids=None) -> dict:
        if not isinstance(scope, str) or scope not in {"current_month", "all"}:
            raise ValueError("Scope must be current_month or all.")

        now = self._now_provider()
        if now.tzinfo is None:
            now = now.replace(tzinfo=APP_TIMEZONE)
        current = now.astimezone(APP_TIMEZONE).date()
        month_start = current.replace(day=1)
        if month_start.month == 12:
            next_month = date(month_start.year + 1, 1, 1)
        else:
            next_month = date(month_start.year, month_start.month + 1, 1)

        statement = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.deleted_at.is_(None),
        )
        if scope == "current_month":
            statement = statement.where(
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date < next_month,
            )
        rows = list(db.session.scalars(statement.order_by(
            Transaction.transaction_date, Transaction.id
        )).all())
        deleted_statement = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.deleted_at.is_not(None),
        )
        if scope == "current_month":
            deleted_statement = deleted_statement.where(
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date < next_month,
            )
        deleted_count = len(db.session.scalars(deleted_statement.with_only_columns(Transaction.id)).all())

        income_total = sum(
            (row.amount for row in rows if row.transaction_type == "income"), Decimal("0.00")
        )
        expense_total = sum(
            (row.amount for row in rows if row.transaction_type == "expense"), Decimal("0.00")
        )
        by_category = {}
        for row in rows:
            key = (row.category.key, row.category.label, row.transaction_type)
            by_category[key] = by_category.get(key, Decimal("0.00")) + row.amount

        missing_context = [
            {
                "id": row.id,
                "transaction_date": row.transaction_date.isoformat(),
                "amount": str(row.amount),
                "category_key": row.category.key,
                "missing": [
                    name for name, value in (
                        ("b_u_c", row.b_u_c),
                        ("reflective_context", row.reflective_context),
                    ) if value is None
                ],
            }
            for row in rows
            if row.transaction_type == "expense" and (row.b_u_c is None or row.reflective_context is None)
        ]

        selected = []
        exclusions = {"soft_deleted": deleted_count, "outside_scope": 0}
        if selected_ids is not None:
            if not isinstance(selected_ids, (list, tuple)):
                raise EvidenceSelectionError("One or more selected transactions are unavailable.")
            ids = list(selected_ids)
            if any(type(value) is not int or value <= 0 for value in ids) or len(ids) != len(set(ids)):
                raise EvidenceSelectionError("One or more selected transactions are unavailable.")
            if ids:
                requested = list(db.session.scalars(select(Transaction).where(
                    Transaction.id.in_(ids), Transaction.user_id == user_id
                )).all())
                by_id = {row.id: row for row in requested}
                if len(by_id) != len(ids) or any(by_id[value].deleted_at is not None for value in ids):
                    raise EvidenceSelectionError("One or more selected transactions are unavailable.")
                scope_ids = {row.id for row in rows}
                if any(value not in scope_ids for value in ids):
                    exclusions["outside_scope"] = sum(value not in scope_ids for value in ids)
                selected = [self._record(by_id[value]) for value in ids]

        if scope == "current_month":
            period = {"start": month_start.isoformat(), "end_exclusive": next_month.isoformat()}
        elif rows:
            period = {
                "start": min(row.transaction_date for row in rows).isoformat(),
                "end_exclusive": (max(row.transaction_date for row in rows) + timedelta(days=1)).isoformat(),
            }
        else:
            period = {"start": None, "end_exclusive": None}

        warnings = []
        if missing_context:
            warnings.append("Some expenses are missing optional context.")
        if deleted_count:
            warnings.append("Soft-deleted transactions are excluded from this scope.")
        if exclusions["outside_scope"]:
            warnings.append("Selected transactions include records outside this aggregate scope.")
        if not rows:
            warnings.append("No transactions are included in this scope.")
        return {
            "scope": scope,
            "timezone": "Europe/Madrid",
            "period": period,
            "source_record_count": len(rows),
            "exclusions": exclusions,
            "warnings": warnings,
            "totals": {
                "income": str(income_total),
                "expense": str(expense_total),
                "net": str(income_total - expense_total),
            },
            "category_totals": [
                {"category_key": key, "category_label": label, "transaction_type": kind, "total": str(total)}
                for (key, label, kind), total in sorted(by_category.items())
            ],
            "expenses_missing_context": missing_context,
            "selected_record_ids": [row["id"] for row in selected],
            "selected_records": selected,
        }

    @staticmethod
    def _record(row: Transaction) -> dict:
        return {
            "id": row.id,
            "transaction_type": row.transaction_type,
            "amount": str(row.amount),
            "transaction_date": row.transaction_date.isoformat(),
            "category_key": row.category.key,
            "category_label": row.category.label,
            "notes": row.notes,
            "b_u_c": row.b_u_c,
            "reflective_context": row.reflective_context,
        }
