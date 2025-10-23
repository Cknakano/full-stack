def test_user_email_must_be_valid(client):
    r = client.post("/api/v1/users/", json={"email":"not-an-email","password":"p"})
    assert r.status_code in (400, 422)

def test_item_wrong_types(client, auth_headers):
    r = client.post("/api/v1/items/", headers=auth_headers,
                    json={"title":123, "description":{"x":"y"}})
    assert r.status_code in (400, 422)
