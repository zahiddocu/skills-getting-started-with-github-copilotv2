import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success():
    # Test signing up for an activity
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]


def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")
    # Second signup should fail
    response = client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_activity_full():
    activity = "Gym Class"
    # Gym Class starts with 2 participants, max 30
    # Add 28 more to fill it
    for i in range(28):
        email = f"user{i}@example.com"
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    # Now try one more, should fail
    response = client.post(f"/activities/{activity}/signup?email=user28@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Activity is full" in data["detail"]
    # This is tricky, perhaps skip or adjust


def test_signup_invalid_activity():
    response = client.post("/activities/Invalid%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Basketball Team"]["participants"]


def test_unregister_not_signed_up():
    response = client.delete("/activities/Drama%20Club/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity():
    response = client.delete("/activities/Invalid%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]