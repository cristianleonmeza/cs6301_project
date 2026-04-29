from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200


def test_auth_and_products_flow():
    with TestClient(app) as client:
        login = client.post("/auth/login", json={"username": "analyst", "password": "analyst123"})
        assert login.status_code == 200
        token = login.json()["access_token"]

        products = client.get("/products", headers={"Authorization": f"Bearer {token}"})
        assert products.status_code == 200
        assert len(products.json()) >= 1