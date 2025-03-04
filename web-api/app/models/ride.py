from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from .waypoint import Waypoint

class Ride(BaseModel):
    name: str
    start_time: str
    end_time: str
    number_waypoints: int = Field(..., ge=0)
    waypoints: List[Waypoint] = []

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format. Expected ISO format: {str(e)}")

    @model_validator(mode='after')
    def validate_waypoint_count(self) -> 'Ride':
        if len(self.waypoints) != self.number_waypoints:
            raise ValueError(f'number_waypoints ({self.number_waypoints}) must match length of waypoints list ({len(self.waypoints)})')
        
        # Also validate that end_time is after start_time
        start = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
        if end < start:
            raise ValueError(f'end_time ({self.end_time}) must be after start_time ({self.start_time})')
        
        return self

    def format_time(self, timestamp: str) -> str:
        """Format ride timestamps for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%I:%M %p, %b %d %Y")
        except:
            return timestamp