import os

import pytest


os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient

from backend.database import Base, SessionLocal, engine
from backend.main import app
from backend.models import Transaction


Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client():
    with SessionLocal() as db:
        db.query(Transaction).delete()
        db.commit()

    with TestClient(app) as test_client:
        yield test_client
