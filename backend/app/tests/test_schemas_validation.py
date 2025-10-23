def test_user_email_must_be_valid(client, auth_headers):
    payload = {"email": "not-an-email", "password": "p"}

    # Try public signup first (some variants expose it)
    r = client.post("/api/v1/users/open", json=payload)
    if r.status_code in (200, 201, 400, 422):
        # if the route exists, ensure invalid email is rejected
        assert r.status_code in (400, 422), f"{r.status_code} {r.text}"
        return

    # Fallback: use admin-only creation with auth
    r2 = client.post("/api/v1/users/", json=payload, headers=auth_headers)
    assert r2.status_code in (400, 422), f"{r2.status_code} {r2.text}"
