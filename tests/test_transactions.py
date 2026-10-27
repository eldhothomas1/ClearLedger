def sample_transaction(**overrides):
    transaction = {
        "date": "2026-10-15",
        "merchant": "Trader Joe's",
        "amount": "48.37",
        "category": "Groceries",
    }
    transaction.update(overrides)
    return transaction


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_transaction_crud(client):
    create_response = client.post("/transactions", json=sample_transaction())
    assert create_response.status_code == 201
    transaction = create_response.json()
    transaction_id = transaction["id"]
    assert transaction["merchant"] == "Trader Joe's"

    get_response = client.get(f"/transactions/{transaction_id}")
    assert get_response.status_code == 200

    update_response = client.patch(
        f"/transactions/{transaction_id}",
        json={"category": "Food"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["category"] == "Food"

    delete_response = client.delete(f"/transactions/{transaction_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/transactions/{transaction_id}").status_code == 404


def test_update_rejects_null_required_field(client):
    transaction_id = client.post(
        "/transactions", json=sample_transaction()
    ).json()["id"]

    response = client.patch(
        f"/transactions/{transaction_id}",
        json={"merchant": None},
    )

    assert response.status_code == 422


def test_list_filters_and_pagination(client):
    client.post("/transactions", json=sample_transaction())
    client.post(
        "/transactions",
        json=sample_transaction(
            date="2026-10-16",
            merchant="Spotify",
            amount="11.99",
            category="Entertainment",
        ),
    )

    response = client.get("/transactions", params={"category": "groceries"})
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 1
    assert body["items"][0]["merchant"] == "Trader Joe's"


def test_create_normalizes_merchant_and_category(client):
    response = client.post(
        "/transactions",
        json=sample_transaction(
            merchant="AMZN Mktp US*AB123",
            category=None,
        ),
    )

    assert response.status_code == 201
    assert response.json()["merchant"] == "Amazon"
    assert response.json()["category"] == "Shopping"


def test_csv_import_reports_duplicates_and_invalid_rows(client):
    csv_data = (
        "date,merchant,amount,category\n"
        "2026-10-01,Chipotle,14.72,Dining\n"
        "2026-10-01,Chipotle,14.72,Dining\n"
        "not-a-date,Target,20.00,Shopping\n"
    )

    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_data, "text/csv")},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["imported"] == 1
    assert body["skipped_duplicates"] == 1
    assert len(body["errors"]) == 1


def test_csv_import_detects_merchant_alias_duplicates(client):
    csv_data = (
        "date,merchant,amount,category\n"
        "2026-10-01,AMZN Mktp US*AB123,24.50,\n"
        "2026-10-01,Amazon Marketplace,24.50,\n"
    )

    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_data, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["imported"] == 1
    assert response.json()["skipped_duplicates"] == 1

    transactions = client.get("/transactions").json()["items"]
    assert transactions[0]["merchant"] == "Amazon"
    assert transactions[0]["category"] == "Shopping"


def test_spending_summary(client):
    client.post("/transactions", json=sample_transaction(amount="40.00"))
    client.post(
        "/transactions",
        json=sample_transaction(
            merchant="Whole Foods",
            amount="60.00",
        ),
    )

    response = client.get("/analytics/summary")
    body = response.json()

    assert response.status_code == 200
    assert body["transaction_count"] == 2
    assert body["total_amount"] == "100.00"
    assert body["average_amount"] == "50.00"
    assert body["by_category"][0]["category"] == "Groceries"


def test_monthly_spending(client):
    client.post(
        "/transactions",
        json=sample_transaction(date="2026-09-12", amount="40.00"),
    )
    client.post(
        "/transactions",
        json=sample_transaction(date="2026-10-04", amount="25.00"),
    )
    client.post(
        "/transactions",
        json=sample_transaction(date="2026-10-20", amount="35.00"),
    )

    response = client.get("/analytics/monthly")

    assert response.status_code == 200
    assert response.json() == [
        {"month": "2026-09", "transaction_count": 1, "total_amount": "40.00"},
        {"month": "2026-10", "transaction_count": 2, "total_amount": "60.00"},
    ]
