"""
Shared fixtures for API endpoint tests.

All tests in test/api/ use a single in-memory SQLite database with a
StaticPool so that every session shares the same connection/data.
Both module-level `crud` singletons in _auth and _games are patched
to use this shared engine before any test runs.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from src.crud import Crud
from src.model import Base

# ---------------------------------------------------------------------------
# One shared engine / crud instance for the entire test/api suite
# ---------------------------------------------------------------------------
_TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_TEST_ENGINE)
_TEST_CRUD = Crud(_TEST_ENGINE)

# Patch module-level singletons BEFORE the app singleton is (re)built
import src.api._auth as _auth_module   # noqa: E402
import src.api._games as _games_module  # noqa: E402

_auth_module.crud = _TEST_CRUD
_games_module.crud = _TEST_CRUD

# Reset the FastAPI app singleton so it is (re)built with the patched routers
import src.api._app as _app_module  # noqa: E402
_app_module._app = None


@pytest.fixture(scope="module")
def client() -> TestClient:
    from src.api import build_app
    app = build_app()
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helper: register + login → Bearer token
# ---------------------------------------------------------------------------
def get_token(client: TestClient, user_name: str, password: str, name: str = "Test User") -> str:
    """Register (ignoring duplicate errors) and return a valid Bearer token."""
    client.post("/auth/register", json={"user_name": user_name, "password": password, "name": name})
    resp = client.post(
        "/auth/login",
        data={"username": user_name, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]
