from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_new_user_recommendation():
    response = client.get(
        "/recommend/999999999?k=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["segment"] == "new_user"
    assert data["count"] == 5

    assert all(
        item["source"]
        == "weighted_popularity_cold_start"
        for item in data["recommendations"]
    )


def test_low_history_recommendation():
    response = client.get(
        "/recommend/1?k=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["segment"] == "low_history"
    assert data["count"] == 5


def test_established_recommendation():
    response = client.get(
        "/recommend/1150086?k=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["segment"] == "established"
    assert data["count"] == 5


def test_invalid_k():
    response = client.get(
        "/recommend/1?k=0"
    )

    assert response.status_code == 400