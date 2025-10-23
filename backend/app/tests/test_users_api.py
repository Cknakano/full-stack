def test_me_endpoint(client, auth_headers):
    r = client.get("/api/v1/users/me", headers=auth_headers)
    assert r.status_code == 200
    assert "email" in r.json()

def test_create_duplicate_user_rejected(client):
    payload = {"email":"dup@ex.com","password":"p"}
    assert client.post("/api/v1/users/", json=payload).status_code in (200, 201)
    r = client.post("/api/v1/users/", json=payload)
    assert r.status_code in (400, 409, 422)
