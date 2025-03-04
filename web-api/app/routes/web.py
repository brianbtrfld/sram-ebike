from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import RideService
from app.models.ride import Ride
import json
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def read_root(request: Request, message: str = None, message_type: str = None):
    """Render the main page with all rides"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "rides": RideService.list_rides(),
            "message": message,
            "message_type": message_type
        }
    )

@router.get("/rides/{ride_id}")
def view_ride_details(request: Request, ride_id: int, message: str = None, message_type: str = None):
    """Render the detailed view for a ride"""
    try:
        ride = RideService.get_ride(ride_id)
        return templates.TemplateResponse(
            "ride_details.html",
            {
                "request": request,
                "ride": ride,
                "ride_id": ride_id,
                "message": message,
                "message_type": message_type
            }
        )
    except:
        return RedirectResponse(
            url="/?message=Ride not found&message_type=error",
            status_code=303
        )

@router.post("/rides/{ride_id}/delete")
async def delete_ride_form(ride_id: int):
    """Delete a ride from form submission"""
    try:
        RideService.delete_ride(ride_id)
        return RedirectResponse(
            url="/?message=Ride deleted successfully&message_type=success",
            status_code=303
        )
    except:
        return RedirectResponse(
            url="/?message=Error deleting ride&message_type=error",
            status_code=303
        )

@router.post("/load-sample")
async def load_sample_ride():
    """Load the sample ride from the samples directory"""
    try:
        sample_path = os.path.join(os.path.dirname(__file__), "..", "samples", "ride_simple.json")
        with open(sample_path, 'r') as file:
            sample_data = json.load(file)
        
        # Convert the JSON data to a Ride model
        sample_ride = Ride(**sample_data)
        RideService.upload_ride(sample_ride)
        
        return RedirectResponse(
            url="/?message=Sample ride loaded successfully&message_type=success",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/?message=Error loading sample ride: {str(e)}&message_type=error",
            status_code=303
        )