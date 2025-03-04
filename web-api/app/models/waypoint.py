from pydantic import BaseModel, field_validator
from datetime import datetime

class Waypoint(BaseModel):
    latitude: float
    longitude: float
    elevation: float
    timestamp: str

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format. Expected ISO format: {str(e)}")

    def format_timestamp(self) -> str:
        """Format the timestamp for display"""
        try:
            dt = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
            return dt.strftime("%I:%M:%S %p")
        except:
            return self.timestamp