def test_create_duplicate_user_rejected(client, auth_headers):
    payload = {"email": "dup@ex.com", "password": "p"}

    # 1) Prefer public signup if this variant exposes it
    r1_open = client.post("/api/v1/users/open", json=payload)
    if r1_open.status_code in (200, 201, 400, 422, 405):  # 405 = method not allowed (no open route)
        if r1_open.status_code in (200, 201):
            # user created via public route; second create (same route if available) must be rejected
            r2_open = client.post("/api/v1/users/open", json=payload)
            assert r2_open.status_code in (400, 409, 422), f"{r2_open.status_code} {r2_open.text}"
            return
        # if public route exists but already rejects the first request as invalid (400/422),
        # that already demonstrates validation; fall back to admin route for duplicate check.

    # 2) Fallback: use admin-only route with auth
    r1_admin = client.post("/api/v1/users/", json=payload, headers=auth_headers)
    assert r1_admin.status_code in (200, 201), f"{r1_admin.status_code} {r1_admin.text}"

    r2_admin = client.post("/api/v1/users/", json=payload, headers=auth_headers)
    assert r2_admin.status_code in (400, 409, 422), f"{r2_admin.status_code} {r2_admin.text}"
