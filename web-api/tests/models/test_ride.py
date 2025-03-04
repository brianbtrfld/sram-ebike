import pytest
from app.models.ride import Ride

def test_ride_timestamp_validation():
    """Test validation of ride timestamps"""
    # Test invalid timestamp format
    with pytest.raises(ValueError) as exc_info:
        Ride(
            name="Test Ride",
            start_time="2024-13-45T25:00:00Z",  # Invalid date/time
            end_time="2024-03-15T11:00:00Z",
            number_waypoints=0,
            waypoints=[]
        )
    assert "Invalid timestamp format" in str(exc_info.value)

    # Test end time before start time
    with pytest.raises(ValueError) as exc_info:
        Ride(
            name="Test Ride",
            start_time="2024-03-15T11:00:00Z",
            end_time="2024-03-15T10:00:00Z",  # Earlier than start_time
            number_waypoints=0,
            waypoints=[]
        )
    assert "end_time" in str(exc_info.value) and "must be after start_time" in str(exc_info.value)

def test_waypoint_count_validation(test_ride):
    """Test validation of waypoint count"""
    # Test with mismatched waypoint count
    invalid_ride = test_ride.copy()
    invalid_ride["number_waypoints"] = 3  # This should fail as we only have 2 waypoints
    
    with pytest.raises(ValueError) as exc_info:
        Ride(**invalid_ride)
    assert "number_waypoints" in str(exc_info.value)