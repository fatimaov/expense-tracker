from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import Category, Transaction, User
from app.routes import v2_routes
from app.services.companion_service import build_companion_evidence, validate_companion_response
from app.services.transaction_evidence_service import TransactionEvidenceService
from app.services.companion_proposal_service import calculate_expected_effect


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
    assert "CompanionProposalResponse" in spec["components"]["schemas"]
    assert "target_transaction_id" in spec["components"]["schemas"]["CompanionQueryRequest"]["properties"]
    assert "proposal_review" in spec["components"]["schemas"]["CompanionQueryRequest"]["properties"]
    assert "/companion/confirm" not in spec["paths"]


def proposal_response(target_id, operation="edit_transaction", fields=None, values=None):
    return {
        "kind": "proposal",
        "message": "I prepared the requested change for review.",
        "missing_or_ambiguous_information": None,
        "proposal": {
            "operation": operation,
            "target_transaction_id": target_id,
            "affected_fields": fields if fields is not None else ["amount"],
            "proposed_values": values if values is not None else {"amount": "15.00"},
            "uncertainty": "The requested amount was clear.",
        },
    }


def test_targeted_companion_returns_transient_proposal_with_deterministic_effect(client, auth_headers, app, companion_rows, monkeypatch):
    provider = FakeGenerator(proposal_response(companion_rows["grocery"]))
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)

    response = client.post("/api/v2/companion/query", json={
        "question": "Please suggest an edit for this record.",
        "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()["data"]
    proposal = data["proposal"]
    assert data["kind"] == "proposal"
    assert proposal["target_transaction_id"] == companion_rows["grocery"]
    assert proposal["proposal_version"] == proposal["current_record"]["updated_at"]
    assert proposal["proposed_values"] == {"amount": "15.00"}
    assert proposal["expected_effect"]["monthly_deltas"] == [{
        "month": "2026-10", "income_delta": "0.00", "expense_delta": "2.50", "net_delta": "-2.50",
        "category_deltas": [{"category_key": "expense_food", "delta": "2.50"}],
    }]
    assert set(provider.call[2]) == {"scope", "timezone", "period", "exclusions", "warnings", "target_transaction"}
    assert "Old shop" not in str(provider.call[2])
    with app.app_context():
        stored = db.session.get(Transaction, companion_rows["grocery"])
        assert str(stored.amount) == "12.50"
        assert stored.deleted_at is None


def test_explicit_amount_change_builds_reviewable_proposal_without_provider(client, auth_headers, app, companion_rows, monkeypatch):
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(
        v2_routes, "create_json_generator",
        lambda settings: pytest.fail("an explicit amount change should not depend on the AI provider"),
    )
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: pytest.fail("no provider request should be recorded"))

    response = client.post("/api/v2/companion/query", json={
        "question": "Change the amount to €18.50",
        "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()["data"]
    proposal = data["proposal"]
    assert data["kind"] == "proposal"
    assert proposal["operation"] == "edit_transaction"
    assert proposal["target_transaction_id"] == companion_rows["grocery"]
    assert proposal["affected_fields"] == ["amount"]
    assert proposal["proposed_values"] == {"amount": "18.50"}
    assert proposal["expected_effect"]["monthly_deltas"][0]["expense_delta"] == "6.00"
    with app.app_context():
        stored = db.session.get(Transaction, companion_rows["grocery"])
        assert str(stored.amount) == "12.50"
        assert stored.deleted_at is None


@pytest.mark.parametrize(("question", "operation", "values"), [
    ("Change the date to 2026-10-06", "edit_transaction", {"transaction_date": "2026-10-06"}),
    ("Change the category to Food", "edit_transaction", {"category_key": "expense_food"}),
    ('Change the notes to "Updated note"', "edit_transaction", {"notes": "Updated note"}),
    ("Delete this transaction", "soft_delete_transaction", {}),
    ("Delete the transaction", "soft_delete_transaction", {}),
    ("Set B/U/C to Choice", "change_transaction_context", {"b_u_c": "choice"}),
    ("Set reflective context to Like", "change_transaction_context", {"reflective_context": "like"}),
    ("Clear B/U/C", "change_transaction_context", {"b_u_c": None}),
    ("Mark this as a Choice and Like", "change_transaction_context", {
        "b_u_c": "choice", "reflective_context": "like",
    }),
])
def test_explicit_transaction_actions_build_reviewable_proposals_without_provider(
    client, auth_headers, app, companion_rows, monkeypatch, question, operation, values,
):
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(
        v2_routes, "create_json_generator",
        lambda settings: pytest.fail("an explicit transaction action should not depend on the AI provider"),
    )
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: pytest.fail("no provider request should be recorded"))

    response = client.post("/api/v2/companion/query", json={
        "question": question,
        "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()["data"]
    proposal = data["proposal"]
    assert data["kind"] == "proposal"
    assert proposal["operation"] == operation
    assert proposal["target_transaction_id"] == companion_rows["grocery"]
    assert proposal["affected_fields"] == list(values)
    assert proposal["proposed_values"] == values
    assert proposal["proposal_version"] == proposal["current_record"]["updated_at"]
    with app.app_context():
        stored = db.session.get(Transaction, companion_rows["grocery"])
        assert str(stored.amount) == "12.50"
        assert stored.deleted_at is None


def test_targeted_companion_clarifies_for_foreign_deleted_and_out_of_scope_targets(client, auth_headers, app, companion_rows, monkeypatch):
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: pytest.fail("unavailable targets must not reach the provider"))
    with app.app_context():
        category = db.session.scalar(select(Category).where(Category.key == "expense_food"))
        other = User(email="other@example.com", password_hash="unused")
        db.session.add(other)
        db.session.flush()
        foreign = Transaction(user_id=other.id, transaction_type="expense", amount="2.00", transaction_date=date(2026, 10, 3), category=category)
        db.session.add(foreign)
        db.session.commit()
        foreign_id = foreign.id

    for target_id in (foreign_id, companion_rows["deleted"], companion_rows["old"], 99999):
        response = client.post("/api/v2/companion/query", json={
            "question": "Please change this record",
            "scope": "current_month",
            "target_transaction_id": target_id,
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["data"]["kind"] == "clarification"


def test_proposal_validation_rejects_wrong_target_extra_fields_and_invalid_values(client, auth_headers, companion_rows, monkeypatch):
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    for invalid in (
        proposal_response(companion_rows["old"]),
        {**proposal_response(companion_rows["grocery"]), "extra": "not allowed"},
        proposal_response(companion_rows["grocery"], values={"amount": "-1"}),
        proposal_response(companion_rows["grocery"], values={"category_key": "unknown"}),
        proposal_response(companion_rows["grocery"], fields=["transaction_date"], values={"transaction_date": "2030-01-01"}),
        proposal_response(companion_rows["grocery"], fields=["transaction_type"], values={"transaction_type": "income"}),
    ):
        provider = FakeGenerator(invalid)
        monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings, provider=provider: provider)
        response = client.post("/api/v2/companion/query", json={
            "question": "Change this record",
            "scope": "current_month",
            "target_transaction_id": companion_rows["grocery"],
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["data"]["kind"] == "clarification"

    income_context = FakeGenerator(proposal_response(
        companion_rows["income"], "change_transaction_context", ["b_u_c"], {"b_u_c": "bill"},
    ))
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: income_context)
    response = client.post("/api/v2/companion/query", json={
        "question": "Set the income context", "scope": "current_month",
        "target_transaction_id": companion_rows["income"],
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["kind"] == "clarification"


def test_context_proposal_is_expense_only_and_category_effect_preserves_financial_totals(client, auth_headers, app, companion_rows, monkeypatch):
    provider = FakeGenerator(proposal_response(
        companion_rows["grocery"], "change_transaction_context", ["b_u_c", "reflective_context"],
        {"b_u_c": "choice", "reflective_context": None},
    ))
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    response = client.post("/api/v2/companion/query", json={
        "question": "Set this expense as a choice",
        "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["proposal"]["expected_effect"] == {
        "kind": "no_financial_change", "message": "Income, expense, and net totals do not change.",
    }

    with app.app_context():
        current = {
            "amount": "12.50", "transaction_date": "2026-10-08", "category_key": "expense_food",
            "transaction_type": "expense",
        }
        effect = calculate_expected_effect(current, "edit_transaction", {"category_key": "expense_other"})
        assert effect["kind"] == "category_reallocation"
        assert effect["monthly_deltas"][0]["income_delta"] == "0.00"
        assert effect["monthly_deltas"][0]["expense_delta"] == "0.00"
        assert effect["monthly_deltas"][0]["category_deltas"] == [
            {"category_key": "expense_food", "delta": "-12.50"},
            {"category_key": "expense_other", "delta": "12.50"},
        ]
        target = db.session.get(Transaction, companion_rows["grocery"])
        assert target.b_u_c is None and target.reflective_context is None


def test_edited_proposal_is_revalidated_and_preview_recalculated_without_provider(client, auth_headers, app, companion_rows, monkeypatch):
    provider = FakeGenerator(proposal_response(companion_rows["grocery"]))
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    initial = client.post("/api/v2/companion/query", json={
        "question": "Change the amount", "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
    }, headers=auth_headers).get_json()["data"]["proposal"]
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: pytest.fail("editing a proposal must not call the provider"))
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: pytest.fail("editing a proposal must not count as an AI request"))
    response = client.post("/api/v2/companion/query", json={
        "question": "Change the amount", "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
        "proposal_review": {
            "operation": initial["operation"],
            "affected_fields": initial["affected_fields"],
            "proposed_values": {"amount": "16.25"},
            "proposal_version": initial["proposal_version"],
            "uncertainty": initial["uncertainty"],
        },
    }, headers=auth_headers)
    assert response.status_code == 200
    updated = response.get_json()["data"]["proposal"]
    assert updated["proposed_values"] == {"amount": "16.25"}
    assert updated["expected_effect"]["monthly_deltas"][0]["expense_delta"] == "3.75"
    assert provider.call is not None
    with app.app_context():
        assert str(db.session.get(Transaction, companion_rows["grocery"]).amount) == "12.50"


def test_edited_proposal_with_stale_version_is_rejected(client, auth_headers, app, companion_rows, monkeypatch):
    provider = FakeGenerator(proposal_response(companion_rows["grocery"]))
    monkeypatch.setattr(v2_routes, "TransactionEvidenceService", lambda: fixed_service())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    proposal = client.post("/api/v2/companion/query", json={
        "question": "Change the amount", "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
    }, headers=auth_headers).get_json()["data"]["proposal"]
    with app.app_context():
        target = db.session.get(Transaction, companion_rows["grocery"])
        target.updated_at = datetime(2026, 10, 9, 12, tzinfo=ZoneInfo("UTC"))
        db.session.commit()
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: pytest.fail("stale edit must not call the provider"))
    response = client.post("/api/v2/companion/query", json={
        "question": "Change the amount", "scope": "current_month",
        "target_transaction_id": companion_rows["grocery"],
        "proposal_review": {
            "operation": proposal["operation"], "affected_fields": proposal["affected_fields"],
            "proposed_values": {"amount": "16.25"}, "proposal_version": proposal["proposal_version"],
            "uncertainty": proposal["uncertainty"],
        },
    }, headers=auth_headers)
    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "STALE_PROPOSAL_VERSION"
