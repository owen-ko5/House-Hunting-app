def register(client, username="alice", email="alice@example.com", password="password123"):
    return client.post("/api/register", json={
        "username": username, "email": email, "password": password,
    })


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_register_and_login(client):
    res = register(client)
    assert res.status_code == 201
    body = res.get_json()
    assert "access_token" in body
    assert body["user"]["username"] == "alice"

    res = client.post("/api/login", json={"email": "alice@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_register_rejects_short_password(client):
    res = client.post("/api/register", json={
        "username": "bob", "email": "bob@example.com", "password": "short",
    })
    assert res.status_code == 422
    assert "password" in res.get_json()["errors"]


def test_duplicate_email_rejected(client):
    register(client)
    res = register(client, username="alice2")
    assert res.status_code == 409


def test_house_requires_auth(client):
    res = client.post("/api/houses", json={"title": "Cozy flat", "location": "Lagos", "price": 1000})
    assert res.status_code == 401


def test_house_create_list_and_ownership(client):
    token = register(client).get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/houses", json={
        "title": "Cozy flat", "location": "Lagos", "price": 1000,
    }, headers=headers)
    assert res.status_code == 201
    house_id = res.get_json()["house"]["id"]

    res = client.get("/api/houses")
    body = res.get_json()
    assert res.status_code == 200
    assert body["total"] == 1
    assert body["houses"][0]["title"] == "Cozy flat"

    # a different user cannot delete alice's listing
    token2 = register(client, username="mallory", email="mallory@example.com").get_json()["access_token"]
    res = client.delete(f"/api/houses/{house_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403

    res = client.delete(f"/api/houses/{house_id}", headers=headers)
    assert res.status_code == 200


def test_pagination_params_validated(client):
    res = client.get("/api/houses?page=not-a-number")
    assert res.status_code == 400
