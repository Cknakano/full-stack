def test_login_success(client):
    client.post("/api/v1/users/", json={"email":"a@ex.com","password":"secret"})
    r = client.post("/api/v1/login/access-token",
                    data={"username":"a@ex.com","password":"secret"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_invalid_password(client):
    client.post("/api/v1/users/", json={"email":"b@ex.com","password":"secret"})
    r = client.post("/api/v1/login/access-token",
                    data={"username":"b@ex.com","password":"WRONG"})
    assert r.status_code in (400, 401, 422)
