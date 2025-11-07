"""Defines the FastAPI router for all weather search CRUD operations."""

from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.weather import (
    DeleteResponse,
    WeatherCreate,
    WeatherDisplay,
    WeatherUpdate,
)
from backend.app.services import weather_service as service

# Initialize the Router
router = APIRouter(
    prefix="/weather",
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=WeatherDisplay,
    status_code=status.HTTP_201_CREATED,
    tags=["Weather Searches"],
)
async def create_weather_search_endpoint(
    request: WeatherCreate, db: Session = Depends(get_db)
):
    """
    **CREATE:** Fetches weather data for the specified location and date range,
    validates, and stores the record in the database.
    """
    # The endpoint is thin: it just calls the service function
    return await service.create_weather_search(db=db, request=request)


@router.get("/", response_model=List[WeatherDisplay], tags=["Weather Searches"])
async def get_all_weather_searches_endpoint(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    **READ:** Retrieves all previous weather searches from the database, paginated.
    """
    return service.get_all_searches(db=db, skip=skip, limit=limit)


@router.get("/{search_id}", response_model=WeatherDisplay, tags=["Weather Searches"])
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


@router.put("/{search_id}", response_model=WeatherDisplay, tags=["Weather Searches"])
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


@router.delete("/{search_id}", response_model=DeleteResponse, tags=["Weather Searches"])
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


@router.get(
    "/export/",
    response_description="Exported weather search data as a file",
    tags=["Data Export"],
)
async def export_weather_searches_endpoint(
    format: Literal["json", "csv"] = Query(
        "csv",
        description="The file format for data export ('json' or 'csv')",
    ),
    db: Session = Depends(get_db),
):
    """
    **READ (Export):** Retrieves all weather searches from the database
    and returns them in the specified file format (JSON or CSV).

    This endpoint returns a file download.
    """

    # 1. Call the service layer to get the data in the correct format
    # The service layer handles all the conversion logic
    export_data = await service.export_searches(db=db, format=format)

    # 2. Prepare the response based on the format
    if format == "json":
        filename = "weather_searches.json"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return JSONResponse(content=export_data, headers=headers)

    if format == "csv":
        filename = "weather_searches.csv"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            iter([export_data]), media_type="text/csv", headers=headers
        )
