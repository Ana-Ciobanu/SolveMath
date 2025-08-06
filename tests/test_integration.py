import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from db.database import Base, get_db
from models.models import User, MathRequest
from controllers.controllers import get_password_hash, router

# Test Database Setup 
TEST_SQLITE_FILE = "./test.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_SQLITE_FILE}"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Ensure no leftover DB
    try:
        os.remove(TEST_SQLITE_FILE)
    except OSError:
        pass
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    admin_pw = get_password_hash("adminpass")
    admin = User(username="superadmin", hashed_password=admin_pw, role="admin")
    db.add(admin)
    db.commit()
    db.close()

    yield

    # Drop tables and delete file
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove(TEST_SQLITE_FILE)
    except OSError:
        pass

# Override get_db dependency to use test DB
@pytest.fixture(autouse=True)
def override_db_dependency(app):
    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

# Initialize FastAPI app and include controller routes
@pytest.fixture(scope="session")
def app():
    app = FastAPI()
    app.include_router(router)
    # Initialize cache
    FastAPICache.init(InMemoryBackend(), prefix="test")
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

# Helper to login and retrieve bearer token
def get_token(client: TestClient, username: str, password: str):
    # Use OAuth2PasswordRequestForm
    data = {"username": username, "password": password}
    resp = client.post("/login", data=data)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]

# Integration Tests
def test_register_and_login(client):
    resp = client.post(
        "/register",
        json={"username": "alice", "password": "alicepass"}
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "User registered successfully"

    token = get_token(client, "alice", "alicepass")
    assert isinstance(token, str)

def test_math_endpoints_and_persistence(client):
    client.post("/register", json={"username": "bob", "password": "bobpass"})
    token = get_token(client, "bob", "bobpass")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/pow",
        headers=headers,
        json={"base": 2, "exponent": 3}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] == 8

    resp = client.post(
        "/fibonacci",
        headers=headers,
        json={"n": 7}
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 13

    resp = client.post(
        "/factorial",
        headers=headers,
        json={"n": 5}
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 120

    db = TestingSessionLocal()
    entries = db.query(MathRequest).all()
    # We should have three entries
    assert len(entries) >= 3
    ops = [e.operation for e in entries]
    assert "pow" in ops and "fibonacci" in ops and "factorial" in ops
    db.close()

def test_rbac_admin_endpoints(client):
    client.post("/register", json={"username": "carol", "password": "carolpass"})
    user_token = get_token(client, "carol", "carolpass")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Normal user cannot access admin endpoints
    for path in ("/admin/requests", "/admin/logs"):
        resp = client.get(path, headers=user_headers)
        assert resp.status_code == 403

    # Login as seeded admin
    admin_token = get_token(client, "superadmin", "adminpass")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin can list requests
    resp = client.get("/admin/requests", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # Admin can list logs
    resp = client.get("/admin/logs", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
