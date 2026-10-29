def transaction(category: str, amount: str, date: str = "2026-10-10"):
    return {
        "date": date,
        "merchant": "Test Merchant",
        "amount": amount,
        "category": category,
    }


def test_budget_tracks_category_spending(client):
    client.post("/transactions", json=transaction("Dining", "40.00"))
    client.post("/transactions", json=transaction("Dining", "15.00"))
    client.post("/transactions", json=transaction("Groceries", "30.00"))

    response = client.put(
        "/budgets",
        json={"month": "2026-10", "category": "Dining", "amount": "100.00"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": response.json()["id"],
        "month": "2026-10",
        "category": "Dining",
        "amount": "100.00",
        "spent": "55.00",
        "remaining": "45.00",
        "percent_used": "55.00",
    }


def test_budget_update_and_delete(client):
    created = client.put(
        "/budgets",
        json={"month": "2026-10", "category": "groceries", "amount": "250.00"},
    ).json()

    updated = client.put(
        "/budgets",
        json={"month": "2026-10", "category": "Groceries", "amount": "300.00"},
    )
    budgets = client.get("/budgets", params={"month": "2026-10"}).json()

    assert updated.json()["id"] == created["id"]
    assert updated.json()["amount"] == "300.00"
    assert len(budgets) == 1

    assert client.delete(f"/budgets/{created['id']}").status_code == 204
    assert client.get("/budgets", params={"month": "2026-10"}).json() == []


def test_budget_rejects_invalid_amount(client):
    response = client.put(
        "/budgets",
        json={"month": "2026-10", "category": "Dining", "amount": "0"},
    )

    assert response.status_code == 422
