import os

import pytest


os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient  # noqa: E402

from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.main import app  # noqa: E402
from backend.models import Transaction  # noqa: E402, F401


Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client():
    with SessionLocal() as db:
        db.query(Transaction).delete()
        db.commit()

    with TestClient(app) as test_client:
        yield test_client
