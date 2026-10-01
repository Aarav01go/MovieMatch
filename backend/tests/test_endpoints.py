import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200


def test_create_user():
    response = client.post("/users", json={"username": "testuser_v2"})
    assert response.status_code == 200
    assert "user_id" in response.json()


def test_get_trending():
    response = client.get("/movies/trending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_rating():
    response = client.post(
        "/ratings", json={"user_id": 1, "movie_id": 1, "rating": 9.0}
    )
    assert response.status_code == 422
