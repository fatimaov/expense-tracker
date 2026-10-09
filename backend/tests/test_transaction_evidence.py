from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import Category, Transaction, User
from app.services.transaction_evidence_service import EvidenceSelectionError, TransactionEvidenceService


def test_current_month_evidence_is_deterministic_owner_scoped_and_explains_exclusions(app):
    now = datetime(2026, 10, 9, 12, tzinfo=ZoneInfo("Europe/Madrid"))
    with app.app_context():
        user_id = app.config["TEST_USER_ID"]
        other_user = User(email="other@example.com", password_hash="unused")
        db.session.add(other_user)
        db.session.flush()
        food = db.session.scalar(select(Category).where(Category.key == "expense_food"))
        salary = db.session.scalar(select(Category).where(Category.key == "income_salary"))
        expense = Transaction(user_id=user_id, transaction_type="expense", amount="12.50",
                              transaction_date=date(2026, 10, 1), category=food, b_u_c=None,
                              reflective_context="need", notes="lunch")
        income = Transaction(user_id=user_id, transaction_type="income", amount="100.00",
                             transaction_date=date(2026, 10, 2), category=salary)
        old = Transaction(user_id=user_id, transaction_type="expense", amount="4.00",
                          transaction_date=date(2026, 9, 30), category=food)
        deleted = Transaction(user_id=user_id, transaction_type="expense", amount="9.00",
                              transaction_date=date(2026, 10, 3), category=food,
                              deleted_at=now)
        foreign = Transaction(user_id=other_user.id, transaction_type="expense", amount="80.00",
                              transaction_date=date(2026, 10, 2), category=food)
        db.session.add_all([expense, income, old, deleted, foreign])
        db.session.commit()
        service = TransactionEvidenceService(now_provider=lambda: now)

        evidence = service.build(user_id, "current_month", selected_ids=[expense.id])
        assert evidence["period"] == {"start": "2026-10-01", "end_exclusive": "2026-11-01"}
        assert evidence["source_record_count"] == 2
        assert evidence["totals"] == {"income": "100.00", "expense": "12.50", "net": "87.50"}
        assert evidence["category_totals"] == [
            {"category_key": "expense_food", "category_label": "Food", "transaction_type": "expense", "total": "12.50"},
            {"category_key": "income_salary", "category_label": "Salary", "transaction_type": "income", "total": "100.00"},
        ]
        assert evidence["exclusions"] == {"soft_deleted": 1, "outside_scope": 0}
        assert evidence["expenses_missing_context"] == [{
            "id": expense.id, "transaction_date": "2026-10-01", "amount": "12.50",
            "category_key": "expense_food", "missing": ["b_u_c"],
        }]
        assert [row["id"] for row in evidence["selected_records"]] == [expense.id]
        assert evidence["selected_records"][0]["notes"] == "lunch"
        with pytest.raises(EvidenceSelectionError):
            service.build(user_id, "all", selected_ids=[foreign.id])
        with pytest.raises(EvidenceSelectionError):
            service.build(user_id, "all", selected_ids=[deleted.id])
        outside_scope = service.build(user_id, "current_month", selected_ids=[old.id])
        assert outside_scope["exclusions"]["outside_scope"] == 1
        assert outside_scope["selected_records"][0]["id"] == old.id

        all_history = service.build(user_id, "all")
        assert all_history["source_record_count"] == 3
        assert all_history["period"] == {"start": "2026-09-30", "end_exclusive": "2026-10-03"}
        assert all_history["timezone"] == "Europe/Madrid"


@pytest.mark.parametrize("selected_id", [99999, -1])
def test_evidence_rejects_missing_or_invalid_selected_records_safely(app, selected_id):
    with app.app_context():
        service = TransactionEvidenceService(now_provider=lambda: datetime(2026, 10, 9, tzinfo=ZoneInfo("Europe/Madrid")))
        with pytest.raises(EvidenceSelectionError) as error:
            service.build(app.config["TEST_USER_ID"], "all", selected_ids=[selected_id])
        assert "unavailable" in str(error.value)


def test_all_history_empty_response_has_null_period_and_warning(app):
    with app.app_context():
        evidence = TransactionEvidenceService().build(app.config["TEST_USER_ID"], "all")
        assert evidence["period"] == {"start": None, "end_exclusive": None}
        assert evidence["source_record_count"] == 0
        assert evidence["warnings"] == ["No transactions are included in this scope."]
