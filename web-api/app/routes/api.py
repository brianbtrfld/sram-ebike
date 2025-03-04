from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from app.models.ride import Ride
from app.services.ride_service import RideService, RideWithSummary

class RideUploadResponse(BaseModel):
    ride: RideWithSummary
    id: int

class RideListResponse(BaseModel):
    ride: RideWithSummary
    id: int

class RideUpdateRequest(BaseModel):
    name: str
    start_time: str
    end_time: str

router = APIRouter(prefix="/api")

@router.post("/rides/upload", response_model=RideUploadResponse)
async def upload_ride(ride: Ride):
    """API endpoint to upload a new ride"""
    return RideService.upload_ride(ride)

@router.get("/rides/{ride_id}", response_model=RideWithSummary)
async def get_ride(ride_id: int):
    """API endpoint to get a specific ride"""
    return RideService.get_ride(ride_id)

@router.get("/rides/", response_model=List[RideListResponse])
async def list_rides():
    """API endpoint to list all rides"""
    return RideService.list_rides()