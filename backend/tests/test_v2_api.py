import json

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
    assert spec["paths"]["/health"]["get"]["security"] == []
    assert spec["paths"]["/categories"]["get"]["security"] == []
    assert "HealthResponse" in spec["components"]["schemas"]
    assert "CategoryListResponse" in spec["components"]["schemas"]
    assert client.get("/api/v2/docs").status_code == 200
