import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(result, dict)
    assert "Chess Club" in result
    assert "description" in result["Chess Club"]
    assert "participants" in result["Chess Club"]
    assert isinstance(result["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Gym Class"
    email = "test.student@mergington.edu"
    url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_bad_request():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate.student@mergington.edu"
    url = f"/activities/{activity_name}/signup?email={email}"

    client.post(url)

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_from_activity_removes_participant():
    # Arrange
    activity_name = "Art Studio"
    email = "remove.student@mergington.edu"
    activities[activity_name]["participants"].append(email)
    url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_bad_request():
    # Arrange
    activity_name = "Science Club"
    email = "not.signedup@mergington.edu"
    url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
