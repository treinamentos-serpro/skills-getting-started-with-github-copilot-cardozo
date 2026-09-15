import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # activities is mutated in place by the endpoints, so restore it after each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_names = set(activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert set(response.json().keys()) == expected_names


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.request("DELETE", f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"

    # Act
    response = client.request("DELETE", f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "michael@mergington.edu"

    # Act
    response = client.request("DELETE", f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_root_redirects_to_static_index():
    # Arrange
    # (no setup needed)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"
