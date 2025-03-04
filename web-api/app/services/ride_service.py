from typing import Dict, List, Any
from fastapi import HTTPException
from app.models.ride import Ride
from app.models.ride_summary import RideSummary
from .ride_summary_calculator import RideSummaryCalculator

class RideWithSummary(Ride):
    summary: RideSummary

class RideService:
    _rides: Dict[int, RideWithSummary] = {}
    _current_id: int = 0

    @classmethod
    def upload_ride(cls, ride: Ride) -> Dict[str, Any]:
        """Upload a new ride, calculate its summary, and return its data with ID"""
        summary = RideSummaryCalculator.calculate_summary(ride.waypoints)
        ride_with_summary = RideWithSummary(**ride.model_dump(), summary=summary)
        
        cls._current_id += 1
        cls._rides[cls._current_id] = ride_with_summary
        return {"ride": ride_with_summary, "id": cls._current_id}

    @classmethod
    def get_ride(cls, ride_id: int) -> RideWithSummary:
        """Get a specific ride by ID"""
        if ride_id not in cls._rides:
            raise HTTPException(status_code=404, detail="Ride not found")
        return cls._rides[ride_id]

    @classmethod
    def update_ride(cls, ride_id: int, name: str, start_time: str, end_time: str) -> RideWithSummary:
        """Update a ride's editable fields (excluding waypoints)"""
        if ride_id not in cls._rides:
            raise HTTPException(status_code=404, detail="Ride not found")
        
        ride = cls._rides[ride_id]
        
        # Create updated ride data while preserving waypoints
        updated_data = ride.model_dump()
        updated_data.update({
            "name": name,
            "start_time": start_time,
            "end_time": end_time
        })
        
        # Validate and update the ride
        updated_ride = RideWithSummary(**updated_data)
        cls._rides[ride_id] = updated_ride
        return updated_ride

    @classmethod
    def list_rides(cls) -> List[Dict[str, Any]]:
        """List all rides with their IDs"""
        return [{"ride": ride, "id": id} for id, ride in cls._rides.items()]

    @classmethod
    def delete_ride(cls, ride_id: int) -> None:
        """Delete a ride by ID"""
        if ride_id not in cls._rides:
            raise HTTPException(status_code=404, detail="Ride not found")
        del cls._rides[ride_id]