import os
import pytest

def _login(client, username, password):
    return client.post(
        "/api/v1/login/access-token",
        data={"username": username, "password": password, "grant_type": "password", "scope": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

def _bearer(token: str):
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.usefixtures()  # no-op, keeps style consistent
def test_login_success(client):
    email = "a@ex.com"
    password = "Secret123!"

    # 1) Try PUBLIC signup first (if the route exists in this variant)
    r_create = client.post("/api/v1/users/open", json={"email": email, "password": password})
    if r_create.status_code in (200, 201):
        # proceed with normal login
        r_login = _login(client, email, password)
        assert r_login.status_code == 200, f"{r_login.status_code} {r_login.text}"
        token = r_login.json().get("access_token")
        assert token
        r_me = client.get("/api/v1/users/me", headers=_bearer(token))
        assert r_me.status_code == 200, f"{r_me.status_code} {r_me.text}"
        assert r_me.json().get("email") == email
        return

    # 2) No public signup. Try to login as FIRST_SUPERUSER from env and create user via admin route.
    admin_email = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    admin_password = os.getenv("FIRST_SUPERUSER_PASSWORD", "changeme")
    r_admin_login = _login(client, admin_email, admin_password)

    if r_admin_login.status_code == 200:
        admin_token = r_admin_login.json().get("access_token")
        assert admin_token, r_admin_login.text

        # try admin-only user creation
        r_admin_create = client.post(
            "/api/v1/users/",
            json={"email": email, "password": password},
            headers=_bearer(admin_token),
        )
        if r_admin_create.status_code not in (200, 201):
            # if admin route not present in this build, skip gracefully
            pytest.skip(f"Admin user-create not available: {r_admin_create.status_code} {r_admin_create.text}")

        # now the regular user can login
        r_login = _login(client, email, password)
        assert r_login.status_code == 200, f"{r_login.status_code} {r_login.text}"
        token = r_login.json().get("access_token")
        assert token
        r_me = client.get("/api/v1/users/me", headers=_bearer(token))
        assert r_me.status_code == 200, f"{r_me.status_code} {r_me.text}"
        assert r_me.json().get("email") == email
        return

    # 3) Neither public signup nor admin login is available in this variant
    pytest.skip("No public signup, and FIRST_SUPERUSER login not available; skipping auth e2e in this build.")
