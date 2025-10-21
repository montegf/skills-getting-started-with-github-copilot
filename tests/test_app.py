from fastapi.testclient import TestClient
import pytest
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Test if the response contains the expected activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    
    # Test structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    
    # Test data types
    assert isinstance(chess_club["description"], str)
    assert isinstance(chess_club["schedule"], str)
    assert isinstance(chess_club["max_participants"], int)
    assert isinstance(chess_club["participants"], list)

def test_signup_success(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify the student was actually added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_already_registered(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already registered
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is already signed up"

def test_signup_activity_not_found(client):
    activity_name = "Non Existent Club"
    email = "newstudent@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_signup_activity_full(client):
    # First, let's fill up an activity
    activity_name = "Chess Club"
    base_email = "test{}@mergington.edu"
    
    # Get current participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    current_participants = len(activities[activity_name]["participants"])
    max_participants = activities[activity_name]["max_participants"]
    
    # Fill up remaining spots
    for i in range(current_participants, max_participants):
        email = base_email.format(i)
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
    
    # Try to add one more student
    response = client.post(f"/activities/{activity_name}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Activity is full"