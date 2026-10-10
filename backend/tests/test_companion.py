from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import Category, Transaction
from app.routes import v2_routes
from app.services.companion_service import build_companion_evidence, validate_companion_response
from app.services.transaction_evidence_service import TransactionEvidenceService


NOW = datetime(2026, 10, 10, 12, tzinfo=ZoneInfo("Europe/Madrid"))


class FakeGenerator:
    def __init__(self, response=None):
        self.response = response or {
            "kind": "answer", "message": "You spent €12.50 in the selected period.",
            "missing_or_ambiguous_information": None,
        }
        self.call = None

    def generate_json(self, instructions, question, evidence, schema):
        self.call = (instructions, question, evidence, schema)
        return self.response


@pytest.fixture()
def companion_rows(app):
    with app.app_context():
        user_id = app.config["TEST_USER_ID"]
        food = db.session.scalar(select(Category).where(Category.key == "expense_food"))
        salary = db.session.scalar(select(Category).where(Category.key == "income_salary"))
        grocery = Transaction(user_id=user_id, transaction_type="expense", amount="12.50",
                              transaction_date=date(2026, 10, 8), category=food,
                              notes="Weekly SHOP SECRET_TRANSACTION_SENTINEL", b_u_c=None)
        income = Transaction(user_id=user_id, transaction_type="income", amount="100.00",
                             transaction_date=date(2026, 10, 2), category=salary)
        old = Transaction(user_id=user_id, transaction_type="expense", amount="7.00",
                          transaction_date=date(2026, 9, 30), category=food, notes="Old shop")
        deleted = Transaction(user_id=user_id, transaction_type="expense", amount="90.00",
                              transaction_date=date(2026, 10, 9), category=food, notes="Deleted SHOP", deleted_at=NOW)
        db.session.add_all([grocery, income, old, deleted])
        db.session.commit()
        return {"grocery": grocery.id, "income": income.id, "old": old.id, "deleted": deleted.id}


def fixed_service():
    return TransactionEvidenceService(now_provider=lambda: NOW)


def test_companion_builds_minimal_aggregate_context_and_madrid_period(app, companion_rows):
    with app.app_context():
        intent, clarification, evidence = build_companion_evidence(
            app.config["TEST_USER_ID"], "current_month", "How much did I spend?", fixed_service()
        )
        assert intent == "expense_total" and clarification is None
        assert evidence["period"] == {"start": "2026-10-01", "end_exclusive": "2026-11-01"}
        assert evidence["total"] == {"expense": "12.50"}
        assert evidence["included_record_count"] == 2
        assert set(evidence) == {"scope", "timezone", "period", "exclusions", "warnings", "included_record_count", "total"}
        assert "records" not in evidence and "category_totals" not in evidence


def test_companion_matching_is_literal_case_insensitive_scoped_and_bounded(app, companion_rows):
    with app.app_context():
        intent, clarification, evidence = build_companion_evidence(
            app.config["TEST_USER_ID"], "current_month", "Find records matching:   sHoP  ", fixed_service()
        )
        assert intent == "matching" and clarification is None
        assert evidence["matching_count"] == 1
        assert [record["id"] for record in evidence["records"]] == [companion_rows["grocery"]]
        assert evidence["records"][0]["notes"].startswith("Weekly SHOP")
        assert companion_rows["deleted"] not in [record["id"] for record in evidence["records"]]
        intent, clarification, _ = build_companion_evidence(
            app.config["TEST_USER_ID"], "current_month", "Find records matching:", fixed_service()
        )
        assert intent is None and clarification


def test_missing_context_evidence_is_bounded_and_match_intent_is_literal(app, companion_rows):
    with app.app_context():
        intent, _, evidence = build_companion_evidence(
            app.config["TEST_USER_ID"], "all", "Show expenses missing optional context", fixed_service()
        )
        assert intent == "missing_context"
        assert evidence["missing_context_count"] == 2
        assert len(evidence["records"]) == 2
        intent, clarification, evidence = build_companion_evidence(
            app.config["TEST_USER_ID"], "all", "Find records matching: shop", fixed_service()
        )
        assert intent == "matching" and clarification is None
        assert evidence["matching_count"] == 2
        assert {record["id"] for record in evidence["records"]} == {companion_rows["grocery"], companion_rows["old"]}


def test_buc_question_excludes_expenses_missing_only_reflective_context(app, companion_rows):
    with app.app_context():
        category = db.session.scalar(select(Category).where(Category.key == "expense_food"))
        reflective_only = Transaction(
            user_id=app.config["TEST_USER_ID"], transaction_type="expense", amount="4.00",
            transaction_date=date(2026, 10, 6), category=category, b_u_c="usage",
        )
        db.session.add(reflective_only)
        db.session.commit()
        intent, clarification, evidence = build_companion_evidence(
            app.config["TEST_USER_ID"], "current_month", "Show expenses missing B/U/C", fixed_service()
        )
        assert intent == "missing_buc" and clarification is None
        assert evidence["missing_context_count"] == 1
        assert [record["id"] for record in evidence["records"]] == [companion_rows["grocery"]]


def test_response_validation_normalizes_common_answer_and_clarification_shapes():
    evidence = {"scope": "current_month", "period": {"start": "2026-10-01", "end_exclusive": "2026-11-01"}}
    answer = validate_companion_response({
        "type": "final", "answer": "You spent €12.50.", "confidence": 0.9,
    }, evidence)
    assert answer["kind"] == "answer"
    assert answer["message"] == "You spent €12.50."
    assert answer["missing_or_ambiguous_information"] is None
    assert answer["evidence"] is evidence

    clarification = validate_companion_response({
        "data": {"type": "clarify", "response": "Which period do you mean?",
                 "missing_information": "Please choose a period."},
    }, evidence)
    assert clarification["kind"] == "clarification"
    assert clarification["message"] == "Which period do you mean?"
    assert clarification["missing_or_ambiguous_information"] == "Please choose a period."


def test_matching_results_are_limited_to_25_newest_with_truncation_warning(app):
    with app.app_context():
        category = db.session.scalar(select(Category).where(Category.key == "expense_food"))
        user_id = app.config["TEST_USER_ID"]
        db.session.add_all([
            Transaction(user_id=user_id, transaction_type="expense", amount="1.00",
                        transaction_date=date(2026, 10, index % 28 + 1), category=category,
                        notes=f"marker {index}")
            for index in range(27)
        ])
        db.session.commit()
        intent, _, evidence = build_companion_evidence(
            user_id, "all", "Find records matching: marker", fixed_service()
        )
        assert intent == "matching"
        assert evidence["matching_count"] == 27
        assert len(evidence["records"]) == 25
        assert evidence["truncated"] is True
        assert evidence["records"][0]["transaction_date"] == "2026-10-27"


def test_response_validation_rejects_proposals_and_malformed_output():
    evidence = {"scope": "all", "period": {"start": None, "end_exclusive": None}}
    valid = validate_companion_response({
        "kind": "answer", "message": "No transactions.", "missing_or_ambiguous_information": None,
    }, evidence)
    assert valid["evidence"] is evidence
    for invalid in (
        {"kind": "proposal", "message": "Change it", "missing_or_ambiguous_information": None},
        {"kind": "answer", "message": "", "missing_or_ambiguous_information": None},
        {"kind": "answer", "message": "Okay", "missing_or_ambiguous_information": None, "evidence": {}},
    ):
        with pytest.raises(ValueError):
            validate_companion_response(invalid, evidence)


def test_companion_api_requires_auth_and_valid_input_before_provider(client, auth_headers, monkeypatch):
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: pytest.fail("provider must not run"))
    assert client.post("/api/v2/companion/query", json={"question": "How much did I spend?", "scope": "all"}).status_code == 401
    for payload in (
        {"question": " ", "scope": "all"},
        {"question": "x" * 1001, "scope": "all"},
        {"question": "How much did I spend?", "scope": "month"},
    ):
        response = client.post("/api/v2/companion/query", json=payload, headers=auth_headers)
        assert response.status_code == 400


def test_companion_api_passes_only_minimal_evidence_and_returns_server_evidence(client, auth_headers, app, companion_rows, monkeypatch, caplog):
    provider = FakeGenerator()
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    response = client.post("/api/v2/companion/query", json={"question": "How much did I spend?", "scope": "current_month"}, headers=auth_headers)
    assert response.status_code == 200
    result = response.get_json()["data"]
    assert result["kind"] == "answer"
    assert result["period"] == {"start": "2026-10-01", "end_exclusive": "2026-11-01"}
    assert result["evidence"]["total"] == {"expense": "12.50"}
    assert "selected_records" not in provider.call[2]
    assert "expenses_missing_context" not in provider.call[2]
    assert "Weekly SHOP" not in str(provider.call[2])
    with app.app_context():
        assert db.session.scalar(select(Transaction).where(Transaction.id == companion_rows["grocery"])).notes == "Weekly SHOP SECRET_TRANSACTION_SENTINEL"
    assert "How much did I spend?" not in caplog.text
    assert "SECRET_TRANSACTION_SENTINEL" not in caplog.text


def test_unsupported_advice_question_gets_clarification_without_provider(client, auth_headers, monkeypatch):
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: pytest.fail("unsupported advice must not reach provider"))
    response = client.post("/api/v2/companion/query", json={
        "question": "Can I afford to reduce my spending?", "scope": "all",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["kind"] == "clarification"


def test_scoped_category_spending_question_is_not_misread_as_full_period_total(app):
    with app.app_context():
        intent, clarification, _ = build_companion_evidence(
            app.config["TEST_USER_ID"], "all", "How much did I spend on food?", fixed_service()
        )
        assert intent is None
        assert "Find records matching" in clarification


def test_unsupported_query_clarifies_and_proposal_output_falls_back_to_server_evidence(client, auth_headers, companion_rows, monkeypatch):
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    unsupported = client.post("/api/v2/companion/query", json={"question": "Tell me about investments", "scope": "all"}, headers=auth_headers)
    assert unsupported.status_code == 200
    assert unsupported.get_json()["data"]["kind"] == "clarification"
    provider = FakeGenerator({"kind": "proposal", "message": "Change", "missing_or_ambiguous_information": None})
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    response = client.post("/api/v2/companion/query", json={"question": "How much did I spend?", "scope": "all"}, headers=auth_headers)
    assert response.status_code == 200
    result = response.get_json()["data"]
    assert result["kind"] == "answer"
    assert "could not be formatted" in result["message"]
    assert result["evidence"]["total"] == {"expense": "19.50"}


def test_companion_openapi_documents_authenticated_answer_contract(client):
    spec = client.get("/api/v2/openapi.json").get_json()
    operation = spec["paths"]["/companion/query"]["post"]
    assert operation["security"] == [{"BearerAuth": []}]
    assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith("CompanionQueryRequest")
    assert "CompanionAnswer" in spec["components"]["schemas"]
    assert "CompanionClarification" in spec["components"]["schemas"]
