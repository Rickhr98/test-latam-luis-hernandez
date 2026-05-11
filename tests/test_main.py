import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_user():
    payload = {
        "username": "jdoe",
        "email": "jdoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "user",
        "active": True,
    }
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["role"] == payload["role"]
    assert data["active"] is True
    assert "id" in data


def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["username"] == "jdoe"


def test_list_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_update_user():
    payload = {"first_name": "Jane", "role": "admin"}
    response = client.put("/users/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["role"] == "admin"


def test_delete_user():
    response = client.delete("/users/1")
    assert response.status_code == 204
    response = client.get("/users/1")
    assert response.status_code == 404


def test_create_duplicate_user():
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "role": "guest",
        "active": True,
    }
    client.post("/users", json=payload)
    response = client.post("/users", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or email already exists"
