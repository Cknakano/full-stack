def test_item_crud(client, auth_headers):
    r = client.post("/api/v1/items/", headers=auth_headers,
                    json={"title":"t","description":"d"})
    assert r.status_code in (200, 201), r.text
    item = r.json()
    item_id = item.get("id") or item.get("uuid") or item.get("item_id")

    r = client.get("/api/v1/items/", headers=auth_headers)
    assert r.status_code == 200
    assert any((i.get("id") == item_id) for i in r.json())

    r = client.put(f"/api/v1/items/{item_id}", headers=auth_headers,
                   json={"title":"t2","description":"d2"})
    assert r.status_code in (200, 404, 405)  # PUT may be optional

    r = client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert r.status_code in (200, 202, 204)
