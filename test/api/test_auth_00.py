"""
Unit tests for authentication API endpoints:
  POST /auth/register
  POST /auth/login
  GET  /auth/me
  PUT  /auth/me
"""
import pytest
from fastapi.testclient import TestClient

from .conftest import get_token


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

def test_register_success(client: TestClient) -> None:
    """Registering a new user returns 201 and the user data."""
    resp = client.post(
        "/auth/register",
        json={"user_name": "auth_user1", "password": "secret1", "name": "Auth User One"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_name"] == "auth_user1"
    assert data["name"] == "Auth User One"
    assert "password" not in data


def test_register_duplicate_username(client: TestClient) -> None:
    """Registering with an already taken username returns 400."""
    client.post(
        "/auth/register",
        json={"user_name": "auth_dup", "password": "pass", "name": "Dup User"},
    )
    resp = client.post(
        "/auth/register",
        json={"user_name": "auth_dup", "password": "pass2", "name": "Dup User2"},
    )
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

def test_login_success(client: TestClient) -> None:
    """Valid credentials return a Bearer access token."""
    client.post(
        "/auth/register",
        json={"user_name": "auth_login1", "password": "mypassword", "name": "Login User"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "auth_login1", "password": "mypassword"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient) -> None:
    """Wrong password returns 401."""
    client.post(
        "/auth/register",
        json={"user_name": "auth_login2", "password": "correct", "name": "Login User 2"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "auth_login2", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client: TestClient) -> None:
    """Unknown username returns 401."""
    resp = client.post(
        "/auth/login",
        data={"username": "nobody_xyz", "password": "pass"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

def test_get_me_success(client: TestClient) -> None:
    """GET /auth/me with valid token returns user info."""
    token = get_token(client, "auth_me1", "pass", "Me User")
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_name"] == "auth_me1"
    assert data["name"] == "Me User"


def test_get_me_no_token(client: TestClient) -> None:
    """GET /auth/me without a token returns 401."""
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_get_me_invalid_token(client: TestClient) -> None:
    """GET /auth/me with a garbage token returns 401."""
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /auth/me
# ---------------------------------------------------------------------------

def test_update_me_success(client: TestClient) -> None:
    """PUT /auth/me updates the display name."""
    token = get_token(client, "auth_update1", "pass", "Old Name")
    resp = client.put(
        "/auth/me",
        json={"name": "New Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["user_name"] == "auth_update1"


def test_update_me_no_token(client: TestClient) -> None:
    """PUT /auth/me without a token returns 401."""
    resp = client.put("/auth/me", json={"name": "Hacker"})
    assert resp.status_code == 401
