import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict to its original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    # Arrange (none needed)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_activities_contains_expected_fields():
    # Arrange (none needed)

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered():
    # Arrange
    email = "michael@mergington.edu"  # pre-seeded in Chess Club

    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_prevents_duplicate_registration():
    # Arrange
    email = "once@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")

    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert activities["Chess Club"]["participants"].count(email) == 1


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"  # pre-seeded in Chess Club

    # Act
    response = client.delete(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/Unknown%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_registered():
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
