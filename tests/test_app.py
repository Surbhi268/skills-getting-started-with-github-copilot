from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_duplicate_signup_returns_400(client):
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    assert response.status_code == 200

    duplicate_response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants?email={quote(email)}"
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_remove_missing_participant_returns_404(client):
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants?email={quote(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_and_remove_on_nonexistent_activity_return_404(client):
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    signup_response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"

    delete_response = client.delete(
        f"/activities/{quote(activity_name)}/participants?email={quote(email)}"
    )
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"
