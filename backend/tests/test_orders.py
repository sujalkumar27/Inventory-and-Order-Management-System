import pytest


@pytest.fixture()
def setup(auth_client):
    client, headers = auth_client
    customer = client.post(
        "/api/customers",
        json={"first_name": "Cust", "last_name": "One", "email": "cust@example.com"},
        headers=headers,
    ).json()
    product = client.post(
        "/api/products",
        json={"sku": "P-1", "name": "Thing", "price": "10.00", "stock_quantity": 10},
        headers=headers,
    ).json()
    return client, headers, customer, product


def test_create_order_deducts_stock_and_totals(setup):
    client, headers, customer, product = setup
    res = client.post(
        "/api/orders",
        json={"customer_id": customer["id"],
              "items": [{"product_id": product["id"], "quantity": 3}]},
        headers=headers,
    )
    assert res.status_code == 201
    order = res.json()
    assert order["total_amount"] == "30.00"
    assert order["status"] == "pending"

    # stock 10 -> 7
    refreshed = client.get(f"/api/products/{product['id']}", headers=headers).json()
    assert refreshed["stock_quantity"] == 7


def test_insufficient_inventory_blocks_order(setup):
    client, headers, customer, product = setup
    res = client.post(
        "/api/orders",
        json={"customer_id": customer["id"],
              "items": [{"product_id": product["id"], "quantity": 12}]},
        headers=headers,
    )
    assert res.status_code == 400
    assert res.json()["message"] == "Insufficient inventory"

    # No order created, stock untouched.
    assert client.get("/api/orders", headers=headers).json()["total"] == 0
    assert client.get(f"/api/products/{product['id']}",
                      headers=headers).json()["stock_quantity"] == 10


def test_cancel_order_restocks(setup):
    client, headers, customer, product = setup
    order = client.post(
        "/api/orders",
        json={"customer_id": customer["id"],
              "items": [{"product_id": product["id"], "quantity": 4}]},
        headers=headers,
    ).json()
    assert client.get(f"/api/products/{product['id']}",
                      headers=headers).json()["stock_quantity"] == 6

    upd = client.put(f"/api/orders/{order['id']}", json={"status": "cancelled"},
                     headers=headers)
    assert upd.status_code == 200 and upd.json()["status"] == "cancelled"
    # restored 6 -> 10
    assert client.get(f"/api/products/{product['id']}",
                      headers=headers).json()["stock_quantity"] == 10


def test_order_invalid_customer(setup):
    client, headers, _, product = setup
    res = client.post(
        "/api/orders",
        json={"customer_id": "00000000-0000-0000-0000-000000000000",
              "items": [{"product_id": product["id"], "quantity": 1}]},
        headers=headers,
    )
    assert res.status_code == 404
