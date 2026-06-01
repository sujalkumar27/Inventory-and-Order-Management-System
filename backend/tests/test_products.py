def _product(sku="SKU-1", name="Widget", price="9.99", stock=100):
    return {"sku": sku, "name": name, "description": "d", "price": price,
            "stock_quantity": stock}


def test_create_product(auth_client):
    client, headers = auth_client
    res = client.post("/api/products", json=_product(), headers=headers)
    assert res.status_code == 201
    assert res.json()["sku"] == "SKU-1"


def test_duplicate_sku(auth_client):
    client, headers = auth_client
    client.post("/api/products", json=_product(), headers=headers)
    res = client.post("/api/products", json=_product(), headers=headers)
    assert res.status_code == 409
    assert res.json()["message"] == "SKU already exists"


def test_negative_price_rejected(auth_client):
    client, headers = auth_client
    res = client.post("/api/products", json=_product(price="-5"), headers=headers)
    assert res.status_code == 422


def test_list_search_and_pagination(auth_client):
    client, headers = auth_client
    for i in range(3):
        client.post("/api/products", json=_product(sku=f"S-{i}", name=f"Item {i}"),
                    headers=headers)
    res = client.get("/api/products?search=Item&page=1&page_size=2", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_update_and_delete(auth_client):
    client, headers = auth_client
    pid = client.post("/api/products", json=_product(), headers=headers).json()["id"]
    upd = client.put(f"/api/products/{pid}", json={"price": "19.99"}, headers=headers)
    assert upd.status_code == 200 and upd.json()["price"] == "19.99"

    dele = client.delete(f"/api/products/{pid}", headers=headers)
    assert dele.status_code == 200
    assert client.get(f"/api/products/{pid}", headers=headers).status_code == 404
