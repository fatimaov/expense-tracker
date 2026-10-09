import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import IdempotencyRecord, Transaction
from app.services.transaction_service import CATEGORY_SEEDS


def test_public_health_and_fixed_categories(client):
    health = client.get("/api/v2/health")
    assert health.status_code == 200
    assert health.get_json() == {"status": "ok"}

    categories = client.get("/api/v2/categories")
    assert categories.status_code == 200
    assert categories.get_json() == {
        "categories": [
            {"key": key, "label": label, "transaction_type": kind}
            for key, label, kind in CATEGORY_SEEDS
        ]
    }


def test_legacy_category_contract_has_five_expense_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert response.get_json() == {"categories": [
        {"key": key, "label": label, "value": label}
        for key, label in [
            ("TRANSPORT", "Transport"),
            ("ACCOMMODATION", "Accommodation"),
            ("FOOD", "Food"),
            ("ACTIVITIES", "Activities"),
            ("OTHER", "Other"),
        ]
    ]}


def test_legacy_expense_crud_uses_transaction_storage(client, auth_headers):
    payload = {
        "amount": "12.34", "title": "Coffee", "expense_date": "2026-01-02",
        "category": "Food", "notes": "With a friend",
    }
    created = client.post("/api/expenses", json=payload, headers=auth_headers)
    assert created.status_code == 201
    expense = created.get_json()["expense"]
    assert expense["title"] == "Coffee"
    assert expense["notes"] == "With a friend"
    expense_id = expense["id"]

    assert client.get("/api/expenses", headers=auth_headers).get_json()["expenses"][0]["id"] == expense_id
    assert client.get(f"/api/expenses/{expense_id}", headers=auth_headers).status_code == 200
    updated = client.put(f"/api/expenses/{expense_id}", json={**payload, "title": "Latte"}, headers=auth_headers)
    assert updated.get_json()["expense"]["title"] == "Latte"
    assert updated.get_json()["expense"]["notes"] == "With a friend"
    assert client.delete(f"/api/expenses/{expense_id}", headers=auth_headers).status_code == 200
    assert client.get(f"/api/expenses/{expense_id}", headers=auth_headers).status_code == 404
    assert client.get("/api/expenses", headers=auth_headers).get_json()["expenses"] == []


def test_openapi_json_and_swagger_ui_are_public(client):
    response = client.get("/api/v2/openapi.json")
    assert response.status_code == 200
    spec = json.loads(response.data)
    assert "/health" in spec["paths"]
    assert "/categories" in spec["paths"]
    assert spec["paths"]["/transactions"]["post"]["security"] == [{"BearerAuth": []}]
    assert spec["paths"]["/transactions"]["post"]["parameters"][0]["name"] == "Idempotency-Key"
    assert "CreateTransactionRequest" in spec["components"]["schemas"]
    assert "CreateTransactionResponse" in spec["components"]["schemas"]
    assert spec["paths"]["/health"]["get"]["security"] == []
    assert spec["paths"]["/categories"]["get"]["security"] == []
    assert "HealthResponse" in spec["components"]["schemas"]
    assert "CategoryListResponse" in spec["components"]["schemas"]
    assert client.get("/api/v2/docs").status_code == 200


def test_create_transaction_requires_authentication(client):
    response = client.post("/api/v2/transactions", json={})
    assert response.status_code == 401


@pytest.mark.parametrize(
    ("transaction_type", "category_key"),
    [("expense", "expense_food"), ("income", "income_salary")],
)
def test_create_transaction_returns_v2_envelope(client, auth_headers, transaction_type, category_key):
    payload = {
        "transaction_type": transaction_type,
        "amount": "12.34",
        "transaction_date": "2026-10-08",
        "category_key": category_key,
        "notes": "Lunch",
    }
    response = client.post(
        "/api/v2/transactions",
        json=payload,
        headers={**auth_headers, "Idempotency-Key": "68aa6d88-f50c-4ec8-bbea-7b5f18c0cbe2"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["data"] == {
        "id": 1,
        "transaction_type": transaction_type,
        "amount": "12.34",
        "transaction_date": "2026-10-08",
        "category_key": category_key,
        "category_label": "Food" if transaction_type == "expense" else "Salary",
        "notes": "Lunch",
        "created_at": body["data"]["created_at"],
        "updated_at": body["data"]["updated_at"],
    }
    assert body["meta"] == {"affected_period_range": {"from": "2026-10", "to": "2026-10"}}


def test_create_transaction_replays_original_result_without_duplicate(client, app, auth_headers):
    key = "1aebc945-645b-4e2b-94f1-92e7bd588e15"
    headers = {**auth_headers, "Idempotency-Key": key}
    payload = {
        "transaction_type": "expense", "amount": "12.34",
        "transaction_date": "2026-10-08", "category_key": "expense_food", "notes": "Lunch",
    }
    first = client.post("/api/v2/transactions", json=payload, headers=headers)
    repeat = client.post("/api/v2/transactions", json={**payload, "notes": "Different"}, headers=headers)

    assert first.status_code == repeat.status_code == 201
    assert repeat.get_json() == first.get_json()
    with app.app_context():
        assert len(db.session.scalars(select(Transaction)).all()) == 1
        assert len(db.session.scalars(select(IdempotencyRecord)).all()) == 1


def test_expired_idempotency_key_can_be_used_again(client, app, auth_headers):
    key = "b485500b-eab1-41c9-9d07-85c79a21dbb7"
    with app.app_context():
        db.session.add(IdempotencyRecord(
            user_id=app.config["TEST_USER_ID"], key=key, response_status=201,
            response_body={"data": {"id": 999}},
            created_at=datetime.now(ZoneInfo("UTC")) - timedelta(hours=25),
        ))
        db.session.commit()
    response = client.post("/api/v2/transactions", json={
        "transaction_type": "income", "amount": "50.00", "transaction_date": "2026-10-08",
        "category_key": "income_salary",
    }, headers={**auth_headers, "Idempotency-Key": key})

    assert response.status_code == 201
    assert response.get_json()["data"]["id"] == 1


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        ({"amount": "1e2"}, "amount"),
        ({"amount": "1.234"}, "amount"),
        ({"amount": "0"}, "amount"),
        ({"amount": "-1"}, "amount"),
        ({"amount": "1000000000000"}, "amount"),
        ({"transaction_date": (datetime.now(ZoneInfo("Europe/Madrid")) + timedelta(days=1)).date().isoformat()}, "transaction_date"),
        ({"transaction_type": "other"}, "transaction_type"),
        ({"category_key": "income_salary"}, "category_key"),
        ({"category_key": "expense_unknown"}, "category_key"),
        ({"transaction_date": "not-a-date"}, "transaction_date"),
        ({"transaction_date": "20261008"}, "transaction_date"),
        ({"b_u_c": None}, "b_u_c"),
        ({"reflective_context": "need"}, "reflective_context"),
        ({"notes": None}, "notes"),
    ],
)
def test_invalid_create_transaction_inputs_use_validation_error_shape(client, auth_headers, updates, field):
    payload = {
        "transaction_type": "expense", "amount": "12.34", "transaction_date": "2026-10-08",
        "category_key": "expense_food", "notes": "Lunch",
    }
    payload.update(updates)
    response = client.post(
        "/api/v2/transactions", json=payload,
        headers={**auth_headers, "Idempotency-Key": "c4dfb365-90d2-46b6-83c4-250eb2e34c53"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"
    assert field in response.get_json()["error"]["fields"]


@pytest.mark.parametrize("payload", [
    {"amount": "12.34", "transaction_date": "2026-10-08", "category_key": "expense_food"},
    {"transaction_type": "expense", "transaction_date": "2026-10-08", "category_key": "expense_food"},
    {"transaction_type": "expense", "amount": "12.34", "category_key": "expense_food"},
    {"transaction_type": "expense", "amount": "12.34", "transaction_date": "2026-10-08"},
])
def test_missing_create_fields_are_rejected(client, auth_headers, payload):
    response = client.post(
        "/api/v2/transactions", json=payload,
        headers={**auth_headers, "Idempotency-Key": "387917d8-87dc-41d0-b24d-a48482c79a3e"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"]["fields"]


def test_missing_or_invalid_idempotency_key_is_rejected(client, auth_headers):
    payload = {
        "transaction_type": "expense", "amount": "12.34", "transaction_date": "2026-10-08",
        "category_key": "expense_food",
    }
    response = client.post("/api/v2/transactions", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "IDEMPOTENCY_KEY_REQUIRED"

    invalid = client.post(
        "/api/v2/transactions", json=payload,
        headers={**auth_headers, "Idempotency-Key": "not-a-uuid"},
    )
    assert invalid.status_code == 400
    assert invalid.get_json()["error"]["fields"]["Idempotency-Key"]
