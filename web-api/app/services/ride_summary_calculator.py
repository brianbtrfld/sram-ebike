from typing import List
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from fastapi import HTTPException
from app.models.waypoint import Waypoint
from app.models.ride_summary import RideSummary

class RideSummaryCalculator:
    """Calculator for generating ride summaries from waypoint data."""

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> None:
        """
        Validate that coordinates are within valid ranges.
        
        Args:
            lat: Latitude in decimal degrees (-90 to 90)
            lon: Longitude in decimal degrees (-180 to 180)
            
        Raises:
            HTTPException: If coordinates are invalid
        """
        if not -90 <= lat <= 90:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid latitude: {lat}. Must be between -90 and 90 degrees."
            )
        if not -180 <= lon <= 180:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid longitude: {lon}. Must be between -180 and 180 degrees."
            )

    @staticmethod
    def validate_timestamps(waypoints: List[Waypoint]) -> None:
        """
        Validate that timestamps are properly formatted and in chronological order.
        
        Args:
            waypoints: List of waypoints to validate
            
        Raises:
            HTTPException: If timestamps are invalid or not chronological
        """
        if not waypoints:
            return

        try:
            timestamps = [datetime.fromisoformat(w.timestamp.replace('Z', '+00:00')) 
                        for w in waypoints]
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid timestamp format. Expected ISO format: {str(e)}"
            )

        # Check chronological order
        if sorted(timestamps) != timestamps:
            raise HTTPException(
                status_code=422,
                detail="Waypoints must be in chronological order"
            )

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on earth in miles.
        
        Args:
            lat1: Latitude of first point in decimal degrees
            lon1: Longitude of first point in decimal degrees
            lat2: Latitude of second point in decimal degrees
            lon2: Longitude of second point in decimal degrees
        
        Returns:
            Distance in miles between the two points
        """
        R = 3959.87433  # Earth's radius in miles

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance

    @staticmethod
    def parse_timestamp(ts: str) -> datetime:
        """
        Parse an ISO format timestamp into a datetime object.
        
        Args:
            ts: ISO format timestamp string
            
        Returns:
            datetime object representing the timestamp
        """
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))

    @classmethod
    def calculate_summary(cls, waypoints: List[Waypoint]) -> RideSummary:
        """
        Calculate a ride summary from a list of waypoints.
        
        Calculates:
        - Total distance in miles
        - Total elevation gain in feet
        - Average speed in mph
        - Max speed in mph
        - Elapsed time as HH:MM:SS
        
        Args:
            waypoints: List of Waypoint objects in chronological order
            
        Returns:
            RideSummary object containing calculated statistics
            
        Raises:
            HTTPException: If waypoint data is invalid or insufficient for calculations
        """
        if not waypoints:
            raise HTTPException(
                status_code=422,
                detail="At least one waypoint is required to calculate ride summary"
            )

        # Validate all waypoint data
        for w in waypoints:
            cls.validate_coordinates(w.latitude, w.longitude)
        cls.validate_timestamps(waypoints)

        total_distance = 0
        total_elevation_gain = 0
        speeds: List[float] = []

        # Sort waypoints by timestamp
        sorted_waypoints = sorted(waypoints, key=lambda w: cls.parse_timestamp(w.timestamp))
        
        # Calculate elapsed time first as we need it for single waypoint case
        start_time = cls.parse_timestamp(sorted_waypoints[0].timestamp)
        end_time = cls.parse_timestamp(sorted_waypoints[-1].timestamp)
        elapsed_delta: timedelta = end_time - start_time
        elapsed_seconds = elapsed_delta.total_seconds()
        hours = int(elapsed_seconds // 3600)
        minutes = int((elapsed_seconds % 3600) // 60)
        seconds = int(elapsed_seconds % 60)
        elapsed_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # For single waypoint, return minimal values
        if len(waypoints) == 1:
            return RideSummary(
                total_distance_mi=0,
                total_elevation_gain_ft=0,
                average_speed_mph=0,
                max_speed_mph=0,
                elapsed_time=elapsed_time
            )

        # Calculate metrics for multiple waypoints
        for i in range(1, len(sorted_waypoints)):
            prev = sorted_waypoints[i-1]
            curr = sorted_waypoints[i]
            
            # Distance calculation
            distance = cls.calculate_distance(
                prev.latitude, prev.longitude,
                curr.latitude, curr.longitude
            )
            total_distance += distance

            # Elevation gain (only positive changes)
            elev_change = curr.elevation - prev.elevation
            if elev_change > 0:
                total_elevation_gain += elev_change

            # Speed calculation
            time_diff = (cls.parse_timestamp(curr.timestamp) - 
                        cls.parse_timestamp(prev.timestamp)).total_seconds() / 3600  # Convert to hours
            if time_diff > 0:
                speed = distance / time_diff
                speeds.append(speed)

        # If no speeds were calculated (all waypoints at same time), use 0
        if not speeds:
            speeds = [0]

        return RideSummary(
            total_distance_mi=round(total_distance, 2),
            total_elevation_gain_ft=round(total_elevation_gain, 1),
            average_speed_mph=round(sum(speeds) / len(speeds), 1),
            max_speed_mph=round(max(speeds), 1),
            elapsed_time=elapsed_time
        )