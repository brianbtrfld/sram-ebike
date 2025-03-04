"""
Data models for GPX processing.
"""

from typing import List, Optional, TypedDict

class Waypoint(TypedDict):
    lat: float
    lon: float
    elevation_ft: float
    timestamp: Optional[str]

class RideData(TypedDict):
    name: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    number_waypoints: int
    total_distance_mi: float
    total_elevation_gain_ft: float
    average_speed_mph: Optional[float]
    max_speed_mph: Optional[float]
    elapsed_time: Optional[str]
    waypoints: List[Waypoint]