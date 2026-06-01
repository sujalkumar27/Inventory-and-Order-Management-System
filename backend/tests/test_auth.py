def test_register_success(client):
    res = client.post(
        "/api/auth/register",
        json={"full_name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "alice@example.com"
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = {"full_name": "Bob", "email": "bob@example.com", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409
    assert res.json()["success"] is False


def test_register_short_password(client):
    res = client.post(
        "/api/auth/register",
        json={"full_name": "C", "email": "c@example.com", "password": "short"},
    )
    assert res.status_code == 422


def test_login_and_refresh(client):
    client.post(
        "/api/auth/register",
        json={"full_name": "Dee", "email": "dee@example.com", "password": "password123"},
    )
    login = client.post(
        "/api/auth/login",
        json={"email": "dee@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"] and tokens["refresh_token"]

    refresh = client.post("/api/auth/refresh",
                          json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"full_name": "Eve", "email": "eve@example.com", "password": "password123"},
    )
    res = client.post("/api/auth/login",
                      json={"email": "eve@example.com", "password": "wrongpass"})
    assert res.status_code == 401


def test_protected_route_requires_auth(client):
    assert client.get("/api/products").status_code == 401
