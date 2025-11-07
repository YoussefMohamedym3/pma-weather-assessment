"""Orchestration layer: Flow control, high-level validation, and coordinating CRUD/API calls."""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..db.models.weather import WeatherSearch

# --- Specialized Imports ---
from ..schemas.weather import WeatherCreate, WeatherUpdate
from .external_apis import get_raw_weather_data_for_range, validate_location_exists
from .weather_crud import (
    create_db_record,
    delete_weather_search,
    get_all_searches,
    get_search_by_id,
    update_db_record,
)
from .weather_extraction import _extract_summary_data_for_db, _filter_raw_data_to_range


def _validate_date_range(date_from: date, date_to: date) -> None:

    if date_from > date_to:
        raise HTTPException(
            status_code=400,
            detail="Validation Error: 'search_date_from' cannot be after 'search_date_to'.",
        )

    today = datetime.now(timezone.utc).date()
    max_forecast_date = today + timedelta(days=13)

    if (date_to - date_from).days > 13:
        raise HTTPException(
            status_code=400,
            detail="Validation Error: Search range cannot exceed 14 days.",
        )

    if date_to > max_forecast_date and date_from >= today:
        raise HTTPException(
            status_code=400,
            detail=f"Validation Error: Forecast cannot extend beyond {max_forecast_date.isoformat()} (14-day API limit).",
        )

    min_history_date = date(2010, 1, 1)
    if date_from < min_history_date:
        raise HTTPException(
            status_code=400,
            detail=f"Validation Error: Historical data is only available from {min_history_date.isoformat()}.",
        )


# --- Orchestrator Functions (The Public API of the Service Layer) ---


async def create_weather_search(db: Session, request: WeatherCreate) -> WeatherSearch:
    """
    Orchestrates the creation of a new weather record: Validates, Fetches, Extracts, and Saves.
    """

    _validate_date_range(request.search_date_from, request.search_date_to)

    # 1. Location Validation/Fuzzy Match
    validated_location_name = await validate_location_exists(request.location_name)

    # 2. Fetch Raw Data
    raw_api_data = await get_raw_weather_data_for_range(
        location=validated_location_name,
        date_from=request.search_date_from,
        date_to=request.search_date_to,
    )

    # 3. Filter and Extract
    filtered_raw_data = _filter_raw_data_to_range(
        raw_api_data, request.search_date_from, request.search_date_to
    )
    summary_data = _extract_summary_data_for_db(filtered_raw_data)

    # 4. Build and Save DB Object
    db_search = WeatherSearch(
        location_name=validated_location_name,
        search_date_from=request.search_date_from,
        search_date_to=request.search_date_to,
        **summary_data,
        raw_forecast_data=filtered_raw_data,
        user_note=None,
        google_maps_url=None,
        youtube_video_ids=None,
    )

    return create_db_record(db, db_search)


async def update_weather_search(
    db: Session, search_id: int, update_data: WeatherUpdate
) -> WeatherSearch:
    """
    Updates a weather search record. Triggers a full data refresh if search parameters change.
    """
    db_search = get_search_by_id(db, search_id)
    if db_search is None:
        raise HTTPException(status_code=404, detail="Search record not found.")

    needs_refresh = (
        update_data.location_name
        or update_data.search_date_from
        or update_data.search_date_to
    )

    if needs_refresh:
        # Use new data if provided, else fall back to existing data
        new_location = update_data.location_name or db_search.location_name
        new_date_from = update_data.search_date_from or db_search.search_date_from
        new_date_to = update_data.search_date_to or db_search.search_date_to

        # --- Re-run the full validation and fetch logic ---
        _validate_date_range(new_date_from, new_date_to)
        validated_location_name = await validate_location_exists(new_location)
        raw_api_data = await get_raw_weather_data_for_range(
            location=validated_location_name,
            date_from=new_date_from,
            date_to=new_date_to,
        )
        filtered_raw_data = _filter_raw_data_to_range(
            raw_api_data, new_date_from, new_date_to
        )
        summary_data = _extract_summary_data_for_db(filtered_raw_data)

        # --- Update all data fields (non-user-note) ---
        db_search.location_name = validated_location_name
        db_search.search_date_from = new_date_from
        db_search.search_date_to = new_date_to
        db_search.raw_forecast_data = filtered_raw_data

        for key, value in summary_data.items():
            setattr(db_search, key, value)

    # Update user_note separately (can be done with or without refresh)
    if update_data.user_note is not None:
        db_search.user_note = update_data.user_note

    return update_db_record(db, db_search)


# --- Public READ/DELETE functions are imported directly from weather_crud ---
# These functions (get_all_searches, delete_weather_search, get_search_by_id)
# are public and exposed by weather_service.py, but their implementation
# resides in weather_crud.py (the DB specialist).

# We must ensure they are properly exported/imported if needed by other modules,
# but for the API endpoint, we will just import them directly from weather_service.py.
