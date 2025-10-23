def test_login_success(client):
    email = "a@ex.com"
    password = "Secret123!"   # strong enough for typical validators

    # 1) create user
    r_create = client.post("/api/v1/users/", json={"email": email, "password": password})
    assert r_create.status_code in (200, 201), r_create.text

    # 2) get access token (OAuth2PasswordRequestForm expects form-encoded body)
    r_login = client.post(
        "/api/v1/login/access-token",
        data={
            "username": email,
            "password": password,
            "grant_type": "password",
            "scope": "",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r_login.status_code == 200, f"{r_login.status_code} {r_login.text}"
    token = r_login.json().get("access_token")
    assert token, r_login.text

    # 3) verify token works on a protected route
    r_me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200, f"{r_me.status_code} {r_me.text}"
    data = r_me.json()
    assert data.get("email") == email
