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

# ---- DB seeding helpers (add to conftest.py) ----
from typing import Optional

def _hash_pw(pw: str) -> str:
    from app.core import security
    return security.get_password_hash(pw)

async def _async_seed_user(email: str, password: str, *, superuser=False) -> None:
    # Async engine/session path
    from sqlmodel import SQLModel
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.db.session import async_engine as engine
    from app.models.user import User

    async with engine.begin() as conn:
        # create tables if not already present (idempotent)
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        # avoid duplicates
        existing = (await session.execute(
            User.__table__.select().where(User.email == email)
        )).first()
        if not existing:
            user = User(
                email=email,
                hashed_password=_hash_pw(password),
                is_active=True,
                is_superuser=bool(superuser),
                full_name="Test User",
            )
            session.add(user)
            await session.commit()

def _sync_seed_user(email: str, password: str, *, superuser=False) -> None:
    # Sync engine/session path
    from sqlmodel import SQLModel, Session
    from app.db.session import engine
    from app.models.user import User

    SQLModel.metadata.create_all(engine)  # idempotent
    with Session(engine) as session:
        existing = session.exec(User.select().where(User.email == email)).first()
        if not existing:
            user = User(
                email=email,
                hashed_password=_hash_pw(password),
                is_active=True,
                is_superuser=bool(superuser),
                full_name="Test User",
            )
            session.add(user)
            session.commit()

def seed_user(email: str, password: str, *, superuser: bool = False) -> None:
    """Seed a user, regardless of async/sync engine."""
    try:
        # try async engine path
        from app.db.session import async_engine as _  # just to detect availability
        asyncio.get_event_loop().run_until_complete(
            _async_seed_user(email, password, superuser=superuser)
        )
    except Exception:
        # fallback to sync engine path
        _sync_seed_user(email, password, superuser=superuser)
# ---- end DB seeding helpers ----

@pytest.fixture
def auth_headers(client):
    email = "u@example.com"
    password = "Secret123!"
    seed_user(email, password, superuser=False)

    r = client.post(
        "/api/v1/login/access-token",
        data={
            "username": email,
            "password": password,
            "grant_type": "password",
            "scope": "",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
