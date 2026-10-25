def test_register_login_and_current_user(public_client):
    register_response = public_client.post(
        "/auth/register",
        json={"email": "eldho@example.com", "password": "securepass123"},
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "eldho@example.com"
    assert "password" not in register_response.json()

    login_response = public_client.post(
        "/auth/login",
        data={"username": "eldho@example.com", "password": "securepass123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    me_response = public_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "eldho@example.com"


def test_duplicate_email_is_rejected(public_client):
    account = {"email": "duplicate@example.com", "password": "securepass123"}
    assert public_client.post("/auth/register", json=account).status_code == 201

    response = public_client.post("/auth/register", json=account)

    assert response.status_code == 409


def test_invalid_login_is_rejected(public_client):
    public_client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "securepass123"},
    )

    response = public_client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_transactions_require_authentication(public_client):
    response = public_client.get("/transactions")

    assert response.status_code == 401


def test_users_cannot_access_each_others_transactions(client, public_client):
    transaction_id = client.post(
        "/transactions",
        json={
            "date": "2026-10-25",
            "merchant": "Chipotle",
            "amount": "14.72",
            "category": "Dining",
        },
    ).json()["id"]

    public_client.headers.pop("Authorization", None)
    public_client.post(
        "/auth/register",
        json={"email": "second@example.com", "password": "securepass123"},
    )
    login_response = public_client.post(
        "/auth/login",
        data={"username": "second@example.com", "password": "securepass123"},
    )
    second_token = login_response.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}

    get_response = public_client.get(
        f"/transactions/{transaction_id}",
        headers=second_headers,
    )
    list_response = public_client.get("/transactions", headers=second_headers)
    summary_response = public_client.get("/analytics/summary", headers=second_headers)

    assert get_response.status_code == 404
    assert list_response.json()["total"] == 0
    assert summary_response.json()["transaction_count"] == 0
