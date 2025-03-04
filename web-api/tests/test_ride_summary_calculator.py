import pytest
from datetime import datetime
from fastapi import HTTPException
from app.models.waypoint import Waypoint
from app.services.ride_summary_calculator import RideSummaryCalculator

def test_empty_waypoints():
    """Test that empty waypoint list raises error"""
    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.calculate_summary([])
    assert "At least one waypoint is required" in str(exc_info.value.detail)

def test_single_waypoint():
    """Test summary calculation with single waypoint"""
    waypoint = Waypoint(
        latitude=37.7749,
        longitude=-122.4194,
        elevation=100.0,
        timestamp="2024-03-15T10:00:00Z"
    )
    summary = RideSummaryCalculator.calculate_summary([waypoint])
    assert summary.total_distance_mi == 0
    assert summary.total_elevation_gain_ft == 0
    assert summary.average_speed_mph == 0  # Now required, defaults to 0
    assert summary.max_speed_mph == 0  # Now required, defaults to 0
    assert summary.elapsed_time == "00:00:00"

def test_distance_calculation():
    """Test distance calculation between two known points"""
    # San Francisco to Oakland
    distance = RideSummaryCalculator.calculate_distance(
        37.7749, -122.4194,  # SF
        37.8044, -122.2712   # Oakland
    )
    assert round(distance, 1) == 8.3  # Verified with Haversine formula

def test_elevation_gain():
    """Test elevation gain calculation"""
    waypoints = [
        Waypoint(latitude=37.7749, longitude=-122.4194, elevation=100.0, timestamp="2024-03-15T10:00:00Z"),
        Waypoint(latitude=37.7750, longitude=-122.4195, elevation=90.0, timestamp="2024-03-15T10:01:00Z"),
        Waypoint(latitude=37.7751, longitude=-122.4196, elevation=110.0, timestamp="2024-03-15T10:02:00Z"),
    ]
    summary = RideSummaryCalculator.calculate_summary(waypoints)
    assert summary.total_elevation_gain_ft == 20.0  # Only counts uphill (110 - 90)

def test_elapsed_time():
    """Test elapsed time calculation"""
    waypoints = [
        Waypoint(latitude=37.7749, longitude=-122.4194, elevation=100.0, timestamp="2024-03-15T10:00:00Z"),
        Waypoint(latitude=37.7750, longitude=-122.4195, elevation=110.0, timestamp="2024-03-15T10:30:00Z"),
        Waypoint(latitude=37.7751, longitude=-122.4196, elevation=120.0, timestamp="2024-03-15T11:15:00Z"),
    ]
    summary = RideSummaryCalculator.calculate_summary(waypoints)
    assert summary.elapsed_time == "01:15:00"  # 1 hour and 15 minutes

def test_speed_calculations():
    """Test average and max speed calculations"""
    # Two 1-mile segments, first taking 30 minutes (2 mph), second taking 15 minutes (4 mph)
    waypoints = [
        Waypoint(latitude=0.0, longitude=0.0, elevation=100.0, timestamp="2024-03-15T10:00:00Z"),
        # ~1 mile north
        Waypoint(latitude=0.014483, longitude=0.0, elevation=110.0, timestamp="2024-03-15T10:30:00Z"),
        # ~1 mile north
        Waypoint(latitude=0.028966, longitude=0.0, elevation=120.0, timestamp="2024-03-15T10:45:00Z"),
    ]
    summary = RideSummaryCalculator.calculate_summary(waypoints)
    assert round(summary.average_speed_mph, 1) == 3.0  # Average of 2 mph and 4 mph
    assert round(summary.max_speed_mph, 1) == 4.0  # Fastest segment was 4 mph

def test_invalid_coordinates():
    """Test validation of invalid coordinates"""
    waypoint = Waypoint(
        latitude=91.0,  # Invalid latitude > 90
        longitude=-122.4194,
        elevation=100.0,
        timestamp="2024-03-15T10:00:00Z"
    )
    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.calculate_summary([waypoint])
    assert "Invalid latitude" in str(exc_info.value.detail)

    waypoint = Waypoint(
        latitude=37.7749,
        longitude=181.0,  # Invalid longitude > 180
        elevation=100.0,
        timestamp="2024-03-15T10:00:00Z"
    )
    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.calculate_summary([waypoint])
    assert "Invalid longitude" in str(exc_info.value.detail)

def test_invalid_timestamp_format():
    """Test validation of invalid timestamp format"""
    from pydantic import ValidationError
    waypoint = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "elevation": 100.0,
        "timestamp": "2024-13-45T25:00:00Z"  # Invalid month/day/hours
    }
    with pytest.raises(ValidationError) as exc_info:
        Waypoint(**waypoint)
    assert "Invalid timestamp format" in str(exc_info.value)

def test_non_chronological_timestamps():
    """Test validation of waypoints not in chronological order"""
    waypoints = [
        Waypoint(latitude=37.7749, longitude=-122.4194, elevation=100.0, timestamp="2024-03-15T10:00:00Z"),
        Waypoint(latitude=37.7750, longitude=-122.4195, elevation=110.0, timestamp="2024-03-15T09:00:00Z"),  # Earlier time
    ]
    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.calculate_summary(waypoints)
    assert "chronological order" in str(exc_info.value.detail)