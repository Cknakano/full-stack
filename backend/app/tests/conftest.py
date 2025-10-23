# ---- test env fallbacks (MUST be before importing app) ----
import os
os.environ.setdefault("PROJECT_NAME", "FastAPI Template")
os.environ.setdefault("SECRET_KEY", "dev-secret")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "app")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("FIRST_SUPERUSER", "admin@example.com")
os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "changeme")
os.environ.setdefault("BACKEND_CORS_ORIGINS", '["http://localhost","http://localhost:3000"]')
# -----------------------------------------------------------

import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app

# If your project exposes async engine & metadata for SQLModel:
try:
    from app.db.session import async_engine as _engine
    from app.db.base import SQLModel as _SQLModel  # metadata
except Exception:
    _engine = None
    _SQLModel = None

@pytest.fixture(scope="session", autouse=True)
def _init_db():
    """Create tables for SQLite test DB before tests, drop after."""
    if _engine and _SQLModel:
        async def _create_all():
            async with _engine.begin() as conn:
                await conn.run_sync(_SQLModel.metadata.create_all)
        asyncio.get_event_loop().run_until_complete(_create_all())
    yield
    if _engine and _SQLModel:
        async def _drop_all():
            async with _engine.begin() as conn:
                await conn.run_sync(_SQLModel.metadata.drop_all)
        asyncio.get_event_loop().run_until_complete(_drop_all())

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers(client):
    email = "u@example.com"
    password = "Secret123!"
    client.post("/api/v1/users/", json={"email": email, "password": password})
    r = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password, "grant_type": "password", "scope": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
