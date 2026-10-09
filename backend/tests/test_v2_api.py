import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import Category, IdempotencyRecord, Transaction, User
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


def _create_transaction(client, auth_headers, amount, transaction_date, category_key="expense_food", kind="expense", key=None):
    import uuid
    return client.post("/api/v2/transactions", json={
        "transaction_type": kind, "amount": amount, "transaction_date": transaction_date,
        "category_key": category_key, "notes": "record",
    }, headers={**auth_headers, "Idempotency-Key": key or str(uuid.uuid4())})


def test_transaction_history_scope_pagination_and_scope_wide_summary(client, app, auth_headers):
    now = datetime.now(ZoneInfo("Europe/Madrid")).date()
    current = now.replace(day=1).isoformat()
    previous = (now.replace(day=1) - timedelta(days=1)).replace(day=1).isoformat()
    assert _create_transaction(client, auth_headers, "10.00", current).status_code == 201
    assert _create_transaction(client, auth_headers, "20.00", now.isoformat()).status_code == 201
    assert _create_transaction(client, auth_headers, "30.00", previous).status_code == 201
    assert _create_transaction(client, auth_headers, "5.00", now.isoformat(), "income_salary", "income").status_code == 201

    page = client.get("/api/v2/transactions?page=1&page_size=1", headers=auth_headers)
    assert page.status_code == 200
    body = page.get_json()
    assert body["meta"]["scope"] == "current_month"
    assert body["meta"]["pagination"] == {"page": 1, "page_size": 1, "total_records": 3, "total_pages": 3}
    assert body["meta"]["summary"] == {
            "record_count": 3, "total_income": "5.00", "total_expense": "30.00",
            "category_totals": [
                {"category_key": "expense_food", "category_label": "Food", "transaction_type": "expense", "total": "30.00"},
                {"category_key": "income_salary", "category_label": "Salary", "transaction_type": "income", "total": "5.00"},
            ],
    }
    all_history = client.get("/api/v2/transactions?scope=all", headers=auth_headers).get_json()
    assert all_history["meta"]["pagination"]["total_records"] == 4
    assert all_history["meta"]["summary"]["total_expense"] == "60.00"
    assert all_history["data"][0]["transaction_date"] == now.isoformat()


def test_transaction_history_validates_query_and_requires_auth(client, auth_headers):
    assert client.get("/api/v2/transactions").status_code == 401
    assert client.get("/api/v2/transactions?page=0", headers=auth_headers).status_code == 400
    assert client.get("/api/v2/transactions?scope=custom", headers=auth_headers).status_code == 400
    assert client.get("/api/v2/transactions?page_size=101", headers=auth_headers).status_code == 400


def test_transaction_history_uses_default_page_size_and_stable_newest_first_order(client, app, auth_headers):
    now = datetime.now(ZoneInfo("Europe/Madrid")).date()
    created = datetime.now(timezone.utc)
    with app.app_context():
        category = db.session.scalar(select(Category).where(Category.key == "expense_food"))
        rows = [Transaction(
            user_id=app.config["TEST_USER_ID"], transaction_type="expense", amount=f"{index + 1}.00",
            transaction_date=now, category=category, notes=f"row-{index}",
            created_at=created + timedelta(seconds=index), updated_at=created + timedelta(seconds=index),
        ) for index in range(26)]
        db.session.add_all(rows)
        db.session.commit()

    first = client.get("/api/v2/transactions?scope=all", headers=auth_headers).get_json()
    second = client.get("/api/v2/transactions?scope=all&page=2", headers=auth_headers).get_json()
    assert first["meta"]["pagination"] == {"page": 1, "page_size": 25, "total_records": 26, "total_pages": 2}
    assert len(first["data"]) == 25
    assert first["data"][0]["notes"] == "row-25"
    assert first["data"][-1]["notes"] == "row-1"
    assert second["data"][0]["notes"] == "row-0"


def test_retrieve_transaction_is_owner_scoped(client, app, auth_headers):
    created = _create_transaction(client, auth_headers, "10.00", "2026-10-08")
    transaction_id = created.get_json()["data"]["id"]
    assert client.get(f"/api/v2/transactions/{transaction_id}", headers=auth_headers).get_json()["data"]["id"] == transaction_id
    with app.app_context():
        other = User(email="other@example.com", password_hash="unused")
        db.session.add(other)
        db.session.commit()
        from flask_jwt_extended import create_access_token
        other_headers = {"Authorization": f"Bearer {create_access_token(identity=str(other.id))}"}
    assert client.get(f"/api/v2/transactions/{transaction_id}", headers=other_headers).status_code == 403
    assert client.get("/api/v2/transactions/9999", headers=auth_headers).status_code == 404


def test_update_transaction_validates_stale_state_and_replays_idempotently(client, app, auth_headers):
    created = _create_transaction(client, auth_headers, "10.00", "2026-10-08")
    data = created.get_json()["data"]
    url = f"/api/v2/transactions/{data['id']}"
    payload = {"amount": "12.50", "transaction_date": "2026-10-07", "category_key": "expense_other", "notes": "Updated", "updated_at": data["updated_at"]}
    key = "2213ab54-34c3-4c55-8ac4-7b93f22318e3"
    updated = client.put(url, json=payload, headers={**auth_headers, "Idempotency-Key": key})
    assert updated.status_code == 200
    assert updated.get_json()["data"]["transaction_type"] == "expense"
    assert updated.get_json()["data"]["amount"] == "12.50"
    assert updated.get_json()["meta"]["affected_period_range"] == {"from": "2026-10", "to": "2026-10"}
    replay = client.put(url, json={**payload, "amount": "99.00"}, headers={**auth_headers, "Idempotency-Key": key})
    assert replay.status_code == 200
    assert replay.get_json() == updated.get_json()

    stale = client.put(url, json={**payload, "updated_at": "2026-01-01T00:00:00+00:00"}, headers={**auth_headers, "Idempotency-Key": "95654c70-c6c9-40db-9dbe-9d06ca63bd6e"})
    assert stale.status_code == 409
    with app.app_context():
        transaction = db.session.get(Transaction, data["id"])
        assert str(transaction.amount) == "12.50"
        assert transaction.notes == "Updated"


@pytest.mark.parametrize("changes,field", [
    ({"transaction_type": "income"}, "transaction_type"),
    ({"b_u_c": "bill"}, "b_u_c"),
    ({"reflective_context": "need"}, "reflective_context"),
    ({"category_key": "income_salary"}, "category_key"),
    ({"amount": "1.234"}, "amount"),
    ({"transaction_date": (datetime.now(ZoneInfo("Europe/Madrid")) + timedelta(days=2)).date().isoformat()}, "transaction_date"),
])
def test_update_transaction_rejects_invalid_fields_without_mutation(client, app, auth_headers, changes, field):
    data = _create_transaction(client, auth_headers, "10.00", "2026-10-08").get_json()["data"]
    payload = {"amount": "11.00", "transaction_date": "2026-10-07", "category_key": "expense_food", "notes": "Updated", "updated_at": data["updated_at"]}
    payload.update(changes)
    response = client.put(f"/api/v2/transactions/{data['id']}", json=payload, headers={**auth_headers, "Idempotency-Key": "2f448885-cc8a-4d7a-87bf-028c0a14c6cc"})
    assert response.status_code == 400
    assert field in response.get_json()["error"]["fields"]
    with app.app_context():
        assert str(db.session.get(Transaction, data["id"]).amount) == "10.00"


def test_delete_transaction_soft_deletes_and_idempotency_replays(client, app, auth_headers):
    data = _create_transaction(client, auth_headers, "10.00", "2026-10-08").get_json()["data"]
    url = f"/api/v2/transactions/{data['id']}"
    key = "70df5c87-7004-428a-ab07-605191cb0eed"
    deleted = client.delete(url, headers={**auth_headers, "Idempotency-Key": key})
    assert deleted.status_code == 200
    assert deleted.get_json() == {"data": {"id": data["id"], "deleted": True}, "meta": {"affected_period_range": {"from": "2026-10", "to": "2026-10"}}}
    replay = client.delete(url, headers={**auth_headers, "Idempotency-Key": key})
    assert replay.status_code == 200
    assert replay.get_json() == deleted.get_json()
    assert client.get(url, headers=auth_headers).status_code == 404
    assert client.get("/api/v2/transactions?scope=all", headers=auth_headers).get_json()["meta"]["summary"]["record_count"] == 0
    with app.app_context():
        assert db.session.get(Transaction, data["id"]).deleted_at is not None


def test_openapi_includes_transaction_history_and_management_contract(client):
    spec = client.get("/api/v2/openapi.json").get_json()
    assert {"get", "post"} <= set(spec["paths"]["/transactions"])
    assert {"get", "put", "delete"} <= set(spec["paths"]["/transactions/{transaction_id}"])
    assert "TransactionListResponse" in spec["components"]["schemas"]
    assert "UpdateTransactionRequest" in spec["components"]["schemas"]
    assert "DeleteTransactionResponse" in spec["components"]["schemas"]
    assert "409" in spec["paths"]["/transactions/{transaction_id}"]["put"]["responses"]
