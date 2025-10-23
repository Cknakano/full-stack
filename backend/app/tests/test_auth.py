def test_login_success(client):
    email = "a@ex.com"
    password = "Secret123!"

    # Seed directly in DB (no HTTP signup needed)
    from app.tests.conftest import seed_user  # or relative import if different
    seed_user(email, password, superuser=False)

    r_login = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password, "grant_type": "password", "scope": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r_login.status_code == 200, f"{r_login.status_code} {r_login.text}"
    token = r_login.json().get("access_token")
    assert token

    r_me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200, f"{r_me.status_code} {r_me.text}"
    assert r_me.json().get("email") == email
