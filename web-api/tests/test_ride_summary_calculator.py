from datetime import datetime
import pytest
from fastapi import HTTPException
from app.models.waypoint import Waypoint
from app.services.ride_summary_calculator import RideSummaryCalculator

def test_empty_waypoints():
    """Test summary calculation with no waypoints"""
    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.calculate_summary([])
    assert exc_info.value.status_code == 422
    assert "At least one waypoint is required" in str(exc_info.value.detail)

def test_single_waypoint():
    """Test summary calculation with single waypoint"""
    waypoint = Waypoint(
        lat=37.7749,
        lon=-122.4194,
        elevation_ft=100.0,
        timestamp="2024-03-15T10:00:00Z"
    )
    summary = RideSummaryCalculator.calculate_summary([waypoint])
    assert summary.total_distance_mi == 0.0
    assert summary.total_elevation_gain_ft == 0.0
    assert summary.elapsed_time == "00:00:00"

def test_distance_calculation():
    """Test distance calculation between two points"""
    waypoints = [
        Waypoint(lat=37.7749, lon=-122.4194, elevation_ft=100.0, timestamp="2024-03-15T10:00:00Z"),
        # About 1 mile north
        Waypoint(lat=37.7897, lon=-122.4194, elevation_ft=100.0, timestamp="2024-03-15T10:30:00Z"),
    ]
    summary = RideSummaryCalculator.calculate_summary(waypoints)
    assert summary.total_distance_mi > 0.9 and summary.total_distance_mi < 1.1

def test_elevation_gain():
    """Test elevation gain calculation"""
    waypoints = [
        Waypoint(lat=37.7749, lon=-122.4194, elevation_ft=100.0, timestamp="2024-03-15T10:00:00Z"),
        Waypoint(lat=37.7750, lon=-122.4195, elevation_ft=90.0, timestamp="2024-03-15T10:01:00Z"),
        Waypoint(lat=37.7751, lon=-122.4196, elevation_ft=110.0, timestamp="2024-03-15T10:02:00Z"),
    ]
    summary = RideSummaryCalculator.calculate_summary(waypoints)
    assert summary.total_elevation_gain_ft == 20.0  # Only positive changes: 0 + 20

def test_elapsed_time():
    """Test elapsed time calculation"""
    waypoints = [
        Waypoint(lat=37.7749, lon=-122.4194, elevation_ft=100.0, timestamp="2024-03-15T10:00:00Z"),
        Waypoint(lat=37.7750, lon=-122.4195, elevation_ft=110.0, timestamp="2024-03-15T10:30:00Z"),
        Waypoint(lat=37.7751, lon=-122.4196, elevation_ft=120.0, timestamp="2024-03-15T11:15:00Z"),
    ]
    summary = RideSummaryCalculator.calculate_summary(waypoints)
    assert summary.elapsed_time == "01:15:00"

def test_speed_calculations():
    """Test average and max speed calculations"""
    # Two 1-mile segments, first taking 30 minutes (2 mph), second taking 15 minutes (4 mph)
    waypoints = [
        Waypoint(lat=0.0, lon=0.0, elevation_ft=100.0, timestamp="2024-03-15T10:00:00Z"),
        # ~1 mile north
        Waypoint(lat=0.014483, lon=0.0, elevation_ft=110.0, timestamp="2024-03-15T10:30:00Z"),
        # ~1 mile north
        Waypoint(lat=0.028966, lon=0.0, elevation_ft=120.0, timestamp="2024-03-15T10:45:00Z"),
    ]
    summary = RideSummaryCalculator.calculate_summary(waypoints)
    assert summary.average_speed_mph == 2.7  # 2 miles / 0.75 hours = 2.666... rounded to 2.7
    assert summary.max_speed_mph == 4.0  # Second segment is 1 mile in 0.25 hours = 4 mph

def test_invalid_coordinates():
    """Test validation of invalid coordinates"""
    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.validate_coordinates(91.0, -122.4194)  # Invalid latitude > 90
    assert exc_info.value.status_code == 422
    assert "Invalid latitude" in str(exc_info.value.detail)

    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.validate_coordinates(37.7749, -200.0)  # Invalid longitude < -180
    assert exc_info.value.status_code == 422
    assert "Invalid longitude" in str(exc_info.value.detail)

def test_invalid_timestamp_format():
    """Test validation of invalid timestamp format"""
    with pytest.raises(ValueError) as exc_info:
        Waypoint(
            lat=37.7749,
            lon=-122.4194,
            elevation_ft=100.0,
            timestamp="2024-13-45T25:00:00Z"  # Invalid date/time
        )
    assert "timestamp" in str(exc_info.value).lower()

def test_non_chronological_timestamps():
    """Test validation of waypoints not in chronological order"""
    waypoints = [
        Waypoint(lat=37.7749, lon=-122.4194, elevation_ft=100.0, timestamp="2024-03-15T10:00:00Z"),
        Waypoint(lat=37.7750, lon=-122.4195, elevation_ft=110.0, timestamp="2024-03-15T09:00:00Z"),  # Earlier time
    ]
    with pytest.raises(HTTPException) as exc_info:
        RideSummaryCalculator.calculate_summary(waypoints)
    assert exc_info.value.status_code == 422
    assert "chronological order" in str(exc_info.value.detail).lower()