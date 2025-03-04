from typing import Optional
from pydantic import BaseModel, Field

class RideSummary(BaseModel):
    total_distance_mi: float = Field(..., ge=0)
    total_elevation_gain_ft: float = Field(..., ge=0)
    average_speed_mph: float = Field(..., ge=0)
    max_speed_mph: float = Field(..., ge=0)
    elapsed_time: str

    def format_elapsed_time(self) -> str:
        """Format elapsed time for display"""
        return self.elapsed_time

    def format_speed(self, speed: float) -> str:
        """Format speed values for display"""
        return f"{speed:.1f} mph"