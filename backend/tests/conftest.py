import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
import app.models  # noqa: F401  register metadata

# Use a dedicated Postgres test DB. CI provides this; locally export TEST_DATABASE_URL.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://ioms:ioms_password@localhost:5432/ioms_test",
)

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_client(client):
    """A client with a registered + logged-in user; returns (client, headers)."""
    client.post(
        "/api/auth/register",
        json={"full_name": "Test User", "email": "test@example.com",
              "password": "password123"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = res.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}
