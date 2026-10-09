from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import AIRequestAttempt, Category, Transaction
from app.services.assisted_entry_service import create_text_transaction_draft


class FakeGenerator:
    def __init__(self, response):
        self.response = response
        self.call = None

    def generate_json(self, system_instructions, user_content, evidence, response_schema):
        self.call = (system_instructions, user_content, evidence, response_schema)
        return self.response


def provider_response(**updates):
    response = {
        "transaction_type": "expense",
        "amount": "12.50",
        "transaction_date": "2026-10-09",
        "category_key": "expense_food",
        "notes": "Lunch",
        "uncertainties": [],
    }
    response.update(updates)
    return response


def test_text_draft_sends_only_text_current_date_and_fixed_categories(app):
    generator = FakeGenerator(provider_response())
    with app.app_context():
        user_id = app.config["TEST_USER_ID"]
        food = db.session.scalar(select(Category).where(Category.key == "expense_food"))
        db.session.add(Transaction(
            user_id=user_id,
            transaction_type="expense",
            amount=Decimal("5.00"),
            transaction_date=datetime(2026, 10, 8, tzinfo=ZoneInfo("Europe/Madrid")).date(),
            category=food,
            notes="Existing private history",
        ))
        db.session.commit()
        result = create_text_transaction_draft(
            "I spent €12.50 on lunch today",
            generator,
            datetime(2026, 10, 9, 23, 30, tzinfo=ZoneInfo("UTC")),
        )
        transactions = db.session.scalars(select(Transaction)).all()

    assert generator.call[1] == "I spent €12.50 on lunch today"
    assert generator.call[2]["current_date"] == "2026-10-10"
    assert {tuple(category.values()) for category in generator.call[2]["categories"]} == {
        (key, label, kind) for key, label, kind in [
            ("expense_transport", "Transport", "expense"),
            ("expense_accommodation", "Accommodation", "expense"),
            ("expense_food", "Food", "expense"),
            ("expense_activities", "Activities", "expense"),
            ("expense_other", "Other", "expense"),
            ("income_salary", "Salary", "income"),
            ("income_other", "Other", "income"),
        ]
    }
    assert "transactions" not in generator.call[2]
    assert "additionalProperties" in generator.call[3]
    assert result["draft"]["amount"] == "12.50"
    assert result["missing_fields"] == []
    assert len(transactions) == 1
    assert transactions[0].notes == "Existing private history"


@pytest.mark.parametrize(("updates", "expected_field"), [
    ({"amount": "12.345"}, "amount"),
    ({"transaction_date": "2026-10-10"}, "transaction_date"),
    ({"category_key": "income_salary"}, "category_key"),
    ({"transaction_type": "transfer"}, "transaction_type"),
])
def test_invalid_provider_values_are_null_and_flagged(app, updates, expected_field):
    generator = FakeGenerator(provider_response(**updates))
    with app.app_context():
        result = create_text_transaction_draft("text unchanged", generator, datetime(2026, 10, 9, tzinfo=ZoneInfo("Europe/Madrid")))
    assert result["draft"][expected_field] is None
    assert any(item["field"] == expected_field for item in result["uncertainties"])
    assert expected_field in result["missing_fields"]


def test_missing_and_uncertain_values_are_returned_for_review(app):
    generator = FakeGenerator(provider_response(
        amount=None,
        uncertainties=[{"field": "transaction_date", "reason": "The date was not stated."}],
    ))
    with app.app_context():
        result = create_text_transaction_draft("Lunch", generator, datetime(2026, 10, 9, tzinfo=ZoneInfo("Europe/Madrid")))
    assert result["draft"]["amount"] is None
    assert result["draft"]["transaction_date"] is None
    assert result["missing_fields"] == ["amount", "transaction_date"]
    assert result["uncertainties"] == [{"field": "transaction_date", "reason": "The date was not stated."}]


@pytest.mark.parametrize(("text", "current", "expected"), [
    ("I paid for lunch yesterday", "2026-10-09", "2026-10-08"),
    ("I paid for lunch the day before yesterday", "2026-10-09", "2026-10-07"),
    ("I paid for lunch last Monday", "2026-10-09", "2026-10-05"),
    ("I paid for lunch last Monday", "2026-10-12", "2026-10-05"),
    ("I paid for lunch today", "2026-10-09", "2026-10-09"),
])
def test_relative_transaction_dates_are_resolved_deterministically(app, text, current, expected):
    generator = FakeGenerator(provider_response(
        transaction_date="2026-10-01",
        uncertainties=[{"field": "transaction_date", "reason": "The model guessed a date."}],
    ))
    with app.app_context():
        result = create_text_transaction_draft(
            text,
            generator,
            datetime.fromisoformat(current).replace(tzinfo=ZoneInfo("Europe/Madrid")),
        )

    assert result["draft"]["transaction_date"] == expected
    assert not any(item["field"] == "transaction_date" for item in result["uncertainties"])


def test_malformed_provider_shape_is_rejected(app):
    generator = FakeGenerator({"transaction_type": "expense"})
    with app.app_context(), pytest.raises(ValueError):
        create_text_transaction_draft("Lunch", generator)


def test_text_draft_api_requires_auth_and_rejects_input_before_provider(client, auth_headers, monkeypatch):
    from app.routes import v2_routes

    provider = FakeGenerator(provider_response())
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: pytest.fail("provider guard should not start"))
    assert client.post("/api/v2/assisted-entry/text", json={"text": "Lunch"}).status_code == 401
    for value in ["", "   ", "x" * 1001]:
        response = client.post("/api/v2/assisted-entry/text", json={"text": value}, headers=auth_headers)
        assert response.status_code == 400
    assert provider.call is None


def test_text_draft_api_uses_guard_and_returns_transient_data_without_mutation(client, app, auth_headers, monkeypatch):
    from app.routes import v2_routes

    provider = FakeGenerator(provider_response())
    guard_calls = []
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: provider)
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: guard_calls.append(user_id))
    response = client.post("/api/v2/assisted-entry/text", json={"text": "  exact user text  "}, headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json()["data"]["draft"]["category_key"] == "expense_food"
    assert provider.call[1] == "  exact user text  "
    assert guard_calls == [app.config["TEST_USER_ID"]]
    with app.app_context():
        assert db.session.scalars(select(Transaction)).all() == []
        assert db.session.scalars(select(AIRequestAttempt)).all() == []


def test_text_draft_api_maps_rate_limit_and_malformed_output_to_safe_errors(client, auth_headers, monkeypatch):
    from app.ai.errors import AIRateLimitExceededError
    from app.routes import v2_routes

    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: FakeGenerator(provider_response()))
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: (_ for _ in ()).throw(AIRateLimitExceededError("Try again later.")))
    limited = client.post("/api/v2/assisted-entry/text", json={"text": "sentinel private input"}, headers=auth_headers)
    assert limited.status_code == 429
    assert "sentinel private input" not in limited.get_data(as_text=True)

    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: FakeGenerator({"bad": "shape"}))
    malformed = client.post("/api/v2/assisted-entry/text", json={"text": "sentinel private input"}, headers=auth_headers)
    assert malformed.status_code == 502
    assert "sentinel private input" not in malformed.get_data(as_text=True)


@pytest.mark.parametrize(("error_type", "expected_status"), [
    ("AIProviderTimeoutError", 504),
    ("AIProviderUnavailableError", 503),
    ("AIConfigurationError", 503),
])
def test_text_draft_api_maps_provider_failures_safely(client, auth_headers, monkeypatch, error_type, expected_status):
    from app.ai import errors
    from app.routes import v2_routes

    class FailingGenerator:
        def generate_json(self, *args, **kwargs):
            raise getattr(errors, error_type)("Safe provider message.")

    monkeypatch.setattr(v2_routes, "create_json_generator", lambda settings: FailingGenerator())
    monkeypatch.setattr(v2_routes, "record_provider_request_start", lambda user_id: None)
    response = client.post("/api/v2/assisted-entry/text", json={"text": "sentinel private input"}, headers=auth_headers)
    assert response.status_code == expected_status
    assert response.get_json()["error"]["message"] == "Safe provider message."
    assert "sentinel private input" not in response.get_data(as_text=True)


def test_openapi_documents_transient_draft_contract(client):
    import json

    spec = json.loads(client.get("/api/v2/openapi.json").data)
    operation = spec["paths"]["/assisted-entry/text"]["post"]
    assert operation["security"] == [{"BearerAuth": []}]
    assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/TextDraftRequest"
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/TextDraftResponse"
    schemas = spec["components"]["schemas"]
    assert set(schemas["TextDraft"]["properties"]) == {
        "transaction_type", "amount", "transaction_date", "category_key", "notes",
    }
    assert schemas["TextDraftRequest"]["properties"]["text"]["maxLength"] == 1000
