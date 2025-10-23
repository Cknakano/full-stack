import pytest
MALICIOUS = [
    "' OR 1=1 --",
    "\"; DROP TABLE users; --",
    "<script>alert(1)</script>",
    "A"*5000,
    "../etc/passwd",
]

@pytest.mark.parametrize("bad", MALICIOUS)
def test_create_item_with_malicious_input(client, auth_headers, bad):
    r = client.post("/api/v1/items/", headers=auth_headers,
                    json={"title": bad, "description": bad})
    # API should not crash; either accept (store) or reject (validate)
    assert r.status_code in (200, 201, 400, 422)
