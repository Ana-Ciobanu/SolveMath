import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from models.models import User, MathRequest
from controllers.controllers import get_password_hash
from app import app

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
        print("Removed old test database file.")
    except OSError as e:
        print(f"Warning: Could not remove test database file. {e}")

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
    except OSError as e:
        print(f"Warning: Could not remove test database file. {e}")


# Override get_db dependency to use test DB
@pytest.fixture(autouse=True)
def override_db_dependency():
    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# Helper to login and return a client with cookies set
def login_with_cookies(client: TestClient, username: str, password: str):
    data = {"username": username, "password": password}
    resp = client.post("/login", data=data)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return client


def test_register_and_login(client):
    resp = client.post("/register", json={"username": "alice", "password": "alicepass"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "User registered successfully"

    # Login and check /me
    login_with_cookies(client, "alice", "alicepass")
    resp = client.get("/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


def test_math_endpoints_and_persistence(client):
    client.post("/register", json={"username": "bob", "password": "bobpass"})
    login_with_cookies(client, "bob", "bobpass")

    resp = client.post("/pow", json={"base": 2, "exponent": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] == 8

    resp = client.post("/fibonacci", json={"n": 7})
    assert resp.status_code == 200
    assert resp.json()["result"] == 13

    resp = client.post("/factorial", json={"n": 5})
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
    login_with_cookies(client, "carol", "carolpass")

    # Normal user cannot access admin endpoints
    for path in ("/admin/requests", "/admin/logs"):
        resp = client.get(path)
        assert resp.status_code == 403

    # Login as seeded admin
    login_with_cookies(client, "superadmin", "adminpass")

    # Admin can list requests
    resp = client.get("/admin/requests")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # Admin can list logs
    resp = client.get("/admin/logs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_metrics_access(client):
    # Register and login as a normal user
    client.post("/register", json={"username": "dave", "password": "davepass"})
    login_with_cookies(client, "dave", "davepass")

    # Normal user should be forbidden
    resp = client.get("/admin/metrics")
    assert resp.status_code == 403

    # Login as seeded admin
    login_with_cookies(client, "superadmin", "adminpass")

    # Admin should have access and receive Prometheus metrics
    resp = client.get("/admin/metrics")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    assert b"# HELP" in resp.content  # Prometheus metrics
