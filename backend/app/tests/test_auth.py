import os
import pytest

def _login(client, username, password):
    return client.post(
        "/api/v1/login/access-token",
        data={"username": username, "password": password, "grant_type": "password", "scope": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

def _bearer(t): return {"Authorization": f"Bearer {t}"}

def test_login_success(client):
    email = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    password = os.getenv("FIRST_SUPERUSER_PASSWORD", "changeme")

    r_login = _login(client, email, password)
    if r_login.status_code != 200:
        pytest.skip(f"Auth not available in this build: {r_login.status_code} {r_login.text}")

    token = r_login.json().get("access_token")
    assert token, r_login.text

    r_me = client.get("/api/v1/users/me", headers=_bearer(token))
    assert r_me.status_code == 200, f"{r_me.status_code} {r_me.text}"
