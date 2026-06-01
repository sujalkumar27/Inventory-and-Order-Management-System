def _customer(email="john@example.com"):
    return {"first_name": "John", "last_name": "Doe", "email": email,
            "phone": "123456", "address": "1 St"}


def test_create_customer(auth_client):
    client, headers = auth_client
    res = client.post("/api/customers", json=_customer(), headers=headers)
    assert res.status_code == 201
    assert res.json()["email"] == "john@example.com"


def test_duplicate_email(auth_client):
    client, headers = auth_client
    client.post("/api/customers", json=_customer(), headers=headers)
    res = client.post("/api/customers", json=_customer(), headers=headers)
    assert res.status_code == 409


def test_update_and_delete_customer(auth_client):
    client, headers = auth_client
    cid = client.post("/api/customers", json=_customer(), headers=headers).json()["id"]
    upd = client.put(f"/api/customers/{cid}", json={"phone": "999"}, headers=headers)
    assert upd.status_code == 200 and upd.json()["phone"] == "999"
    assert client.delete(f"/api/customers/{cid}", headers=headers).status_code == 200
    assert client.get(f"/api/customers/{cid}", headers=headers).status_code == 404


def test_search_customers(auth_client):
    client, headers = auth_client
    client.post("/api/customers", json=_customer("a@example.com"), headers=headers)
    client.post("/api/customers", json=_customer("b@example.com"), headers=headers)
    res = client.get("/api/customers?search=john", headers=headers)
    assert res.json()["total"] == 2
