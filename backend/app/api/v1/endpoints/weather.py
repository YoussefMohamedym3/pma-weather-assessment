"""Defines the FastAPI router for all weather search CRUD operations."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db

# --- CORRECTED IMPORTS ---
from backend.app.schemas.weather import (
    DeleteResponse,
    WeatherCreate,
    WeatherDisplay,
    WeatherUpdate,
)
from backend.app.services import weather_service as service

# File: backend/app/api/v1/endpoints/weather.py (Corrected Imports)


# --- END CORRECTED IMPORTS ---

# ... rest of the file content ...

# Initialize the Router
router = APIRouter(
    prefix="/weather",
    tags=["Weather Searches"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=WeatherDisplay, status_code=status.HTTP_201_CREATED)
async def create_weather_search_endpoint(
    request: WeatherCreate, db: Session = Depends(get_db)
):
    """
    **CREATE:** Fetches weather data for the specified location and date range,
    validates, and stores the record in the database.
    """
    # The endpoint is thin: it just calls the service function
    return await service.create_weather_search(db=db, request=request)


@router.get("/", response_model=List[WeatherDisplay])
async def get_all_weather_searches_endpoint(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    **READ:** Retrieves all previous weather searches from the database, paginated.
    """
    return service.get_all_searches(db=db, skip=skip, limit=limit)


@router.get("/{search_id}", response_model=WeatherDisplay)
async def get_weather_search_by_id_endpoint(
    search_id: int = Path(..., description="ID of the search record to retrieve"),
    db: Session = Depends(get_db),
):
    """
    **READ ONE:** Retrieves a single weather search record by its unique ID.
    """
    # The service function handles the 404 error internally if the record is missing.
    db_search = service.get_search_by_id(db=db, search_id=search_id)
    if db_search is None:
        raise HTTPException(status_code=404, detail="Search record not found.")
    return db_search


@router.put("/{search_id}", response_model=WeatherDisplay)
async def update_weather_search_endpoint(
    update_data: WeatherUpdate,
    search_id: int = Path(..., description="ID of the search record to update"),
    db: Session = Depends(get_db),
):
    """
    **UPDATE:** Updates search parameters (location/dates, which triggers re-validation/API refresh)
    or just the user note.
    """
    return await service.update_weather_search(
        db=db, search_id=search_id, update_data=update_data
    )


@router.delete("/{search_id}", response_model=DeleteResponse)
async def delete_weather_search_endpoint(
    search_id: int = Path(..., description="ID of the search record to delete"),
    db: Session = Depends(get_db),
):
    """
    **DELETE:** Deletes a weather search record from the database.
    """
    # The service function handles the 404 error internally.
    service.delete_weather_search(db=db, search_id=search_id)
    return {"message": f"Search record {search_id} deleted successfully."}
