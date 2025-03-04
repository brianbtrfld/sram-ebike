from fastapi.testclient import TestClient

def test_upload_ride(client, test_ride):
    response = client.post("/api/rides/upload", json=test_ride)
    assert response.status_code == 200
    result = response.json()
    
    # Verify basic ride data
    assert "id" in result
    assert result["ride"]["name"] == test_ride["name"]
    assert result["ride"]["start_time"] == test_ride["start_time"]
    assert result["ride"]["end_time"] == test_ride["end_time"]
    assert len(result["ride"]["waypoints"]) == test_ride["number_waypoints"]
    
    # Verify summary was calculated
    assert "summary" in result["ride"]
    summary = result["ride"]["summary"]
    assert summary["total_distance_mi"] > 0
    assert summary["total_elevation_gain_ft"] == 10.0
    assert summary["elapsed_time"] == "00:05:00"
    assert summary["average_speed_mph"] > 0
    assert summary["max_speed_mph"] > 0

def test_get_ride(client, created_ride):
    response = client.get(f"/api/rides/{created_ride}")
    assert response.status_code == 200
    ride = response.json()
    
    # Verify ride data includes summary
    assert ride["name"] == "Test Ride"
    assert "summary" in ride
    assert ride["summary"]["total_distance_mi"] > 0
    assert ride["summary"]["total_elevation_gain_ft"] == 10.0
    assert len(ride["waypoints"]) == 2

def test_get_nonexistent_ride(client):
    response = client.get("/api/rides/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ride not found"

def test_list_rides(client, created_ride, test_ride):
    # Create a second ride to ensure we have at least two
    response = client.post("/api/rides/upload", json=test_ride)
    assert response.status_code == 200
    
    response = client.get("/api/rides/")
    assert response.status_code == 200
    rides = response.json()
    assert len(rides) >= 2
    assert all(isinstance(ride["id"], int) for ride in rides)
    assert all("ride" in ride for ride in rides)
    assert all("summary" in ride["ride"] for ride in rides)
    assert all("waypoints" in ride["ride"] for ride in rides)

def test_required_fields(client):
    # Test missing required fields
    incomplete_ride = {
        "name": "Test Ride",
        "waypoints": []
    }
    response = client.post("/api/rides/upload", json=incomplete_ride)
    assert response.status_code == 422  # Unprocessable Entity