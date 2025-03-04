import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ride_service import RideService

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def ride_service():
    # Clear rides before each test
    RideService._rides.clear()
    RideService._current_id = 0
    return RideService

@pytest.fixture
def test_waypoints():
    return [
        {
            "latitude": 37.774929,
            "longitude": -122.419416,
            "elevation": 100.0,
            "timestamp": "2024-03-15T10:00:00Z"
        },
        {
            "latitude": 37.775929,
            "longitude": -122.429416,
            "elevation": 110.0,
            "timestamp": "2024-03-15T10:05:00Z"
        }
    ]

@pytest.fixture
def test_summary():
    return {
        "total_distance_mi": 15.5,
        "total_elevation_gain_ft": 500.0,
        "average_speed_mph": 15.5,
        "max_speed_mph": 25.0,
        "elapsed_time": "1:00:00"
    }

@pytest.fixture
def test_ride(test_waypoints):
    return {
        "name": "Test Ride",
        "start_time": "2024-03-15T10:00:00Z",
        "end_time": "2024-03-15T10:05:00Z",
        "number_waypoints": len(test_waypoints),
        "waypoints": test_waypoints
    }

@pytest.fixture
def created_ride(client, test_ride):
    """Creates a test ride and returns its ID"""
    response = client.post("/api/rides/upload", json=test_ride)
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    return result["id"]