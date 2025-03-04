"""
Utility functions for GPX processing and calculations.
"""

from typing import List
from math import asin, cos, radians, sin, sqrt

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using the Haversine formula.
    Returns distance in miles.
    """
    R = 3959.0  # Earth's radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def calculate_elevation_gain(elevations_ft: List[float]) -> float:
    """Calculate total elevation gain in feet from a list of elevation points."""
    gain = 0
    for i in range(1, len(elevations_ft)):
        diff = elevations_ft[i] - elevations_ft[i-1]
        if diff > 0:  # Only count elevation gains
            gain += diff
    return gain

def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters * 3.28084

def format_elapsed_time(seconds: float) -> str:
    """Format elapsed time in seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def is_valid_speed(speed: float, prev_speed: float = None) -> bool:
    """
    Validate if a calculated speed value is realistic.
    
    Args:
        speed: Speed in mph
        prev_speed: Previous valid speed for comparison, if available
    
    Returns:
        bool: True if speed seems valid, False otherwise
    """
    MAX_REASONABLE_SPEED = 45.0  # mph
    MAX_ACCELERATION = 10.0  # mph change per reading

    if speed < 0 or speed > MAX_REASONABLE_SPEED:
        return False
        
    if prev_speed is not None:
        if abs(speed - prev_speed) > MAX_ACCELERATION:
            return False
            
    return True