from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import RideService

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

@router.get("/rides/{ride_id}/edit")
def edit_ride_form(request: Request, ride_id: int):
    """Render the edit form for a ride"""
    try:
        ride = RideService.get_ride(ride_id)
        return templates.TemplateResponse(
            "edit_ride.html",
            {
                "request": request,
                "ride": ride,
                "ride_id": ride_id
            }
        )
    except:
        return RedirectResponse(
            url="/?message=Ride not found&message_type=error",
            status_code=303
        )

@router.post("/rides/{ride_id}/edit")
async def update_ride_form(
    ride_id: int,
    name: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...)
):
    """Update a ride from form submission"""
    try:
        RideService.update_ride(ride_id, name, start_time, end_time)
        return RedirectResponse(
            url="/?message=Ride updated successfully&message_type=success",
            status_code=303
        )
    except ValueError as e:
        return RedirectResponse(
            url=f"/rides/{ride_id}/edit?message={str(e)}&message_type=error",
            status_code=303
        )
    except:
        return RedirectResponse(
            url="/?message=Error updating ride&message_type=error",
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
            url="/?message=Ride not found&message_type=error",
            status_code=303
        )