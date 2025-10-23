def test_login_success(client):
    # use a strong password to avoid policy/validation issues
    email = "a@ex.com"
    password = "Secret123!"   # >=8 chars, mixed

    # create user
    r_create = client.post("/api/v1/users/", json={"email": email, "password": password})
    assert r_create.status_code in (200, 201), r_create.text

    # login: form-encoded body expected by OAuth2PasswordRequestForm
    r_login = client.post(
        "/api/v1/login/access-token",
        data={
            "username": email,
            "password": password,
            "grant_type": "password",
            "scope": "",            # optional but harmless
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r_login.status_code == 200, r_login.text
    data = r_login.json()
    assert "access_token" in data and data["access_token"]
