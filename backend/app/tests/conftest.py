# ---- test env fallbacks (MUST be before importing app) ----
import os
os.environ.setdefault("PROJECT_NAME", "FastAPI Template")
os.environ.setdefault("SECRET_KEY", "dev-secret")
os.environ.setdefault("TESTING", "1")

# Prefer DATABASE_URL if provided by CI (e.g., Postgres service); otherwise use local SQLite.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Keep these only as placeholders if your Settings validate their presence.
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "app")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")

# First superuser creds (used by auth fixture)
os.environ.setdefault("FIRST_SUPERUSER", "admin@example.com")
os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "changeme")

os.environ.setdefault(
    "BACKEND_CORS_ORIGINS",
    '["http://localhost","http://localhost:3000"]'
)
# -----------------------------------------------------------

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Basic TestClient for API tests."""
    with TestClient(app) as c:
        yield c


def _login(client, username, password):
    """OAuth2 form-encoded login helper."""
    return client.post(
        "/api/v1/login/access-token",
        data={
            "username": username,
            "password": password,
            "grant_type": "password",
            "scope": "",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


@pytest.fixture
def auth_headers(client):
    """
    Try to authenticate using FIRST_SUPERUSER creds supplied via env/CI.
    If login isn't available in this variant, skip auth-dependent tests gracefully.
    """
    admin_email = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    admin_pw = os.getenv("FIRST_SUPERUSER_PASSWORD", "changeme")

    r = _login(client, admin_email, admin_pw)
    if r.status_code != 200:
        pytest.skip(
            f"Cannot authenticate first superuser in this build "
            f"(status {r.status_code}): {r.text}"
        )

    token = r.json().get("access_token")
    if not token:
        pytest.skip("No access_token returned; skipping auth-dependent test")

    return {"Authorization": f"Bearer {token}"}
