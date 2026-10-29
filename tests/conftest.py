import os

import pytest


os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-clearledger-authentication"

from fastapi.testclient import TestClient

from backend.database import Base, SessionLocal, engine
from backend.main import app
from backend.models import Budget, Transaction, User


Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_database():
    with SessionLocal() as db:
        db.query(Budget).delete()
        db.query(Transaction).delete()
        db.query(User).delete()
        db.commit()

    yield


@pytest.fixture()
def public_client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def client(public_client):
    public_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    login_response = public_client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    public_client.headers.update({"Authorization": f"Bearer {token}"})

    yield public_client
