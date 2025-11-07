"""Orchestration layer: Flow control, high-level validation, and coordinating CRUD/API calls."""

# --- Standard Library Imports ---
import csv
import io
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# --- Third-Party Imports ---
from fastapi import HTTPException
from sqlalchemy.orm import Session

# --- Project-Specific Imports ---
from ..db.models.weather import WeatherSearch
from ..schemas.weather import WeatherCreate, WeatherUpdate
from .external_apis import (
    get_raw_weather_data_for_range,
    get_youtube_videos,
    validate_location_exists,
)
from .weather_crud import get_all_searches_unpaginated  # <-- ADD THIS IMPORT
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

    # 3.5. Fetch External API Data (Task 2.2)
    youtube_video_ids = await get_youtube_videos(validated_location_name)

    # --- Google Maps Workaround (No API Key Needed) ---
    google_maps_url = None
    location_data = raw_api_data.get("location")
    if location_data:
        lat = location_data.get("lat")
        lon = location_data.get("lon")
        if lat and lon:
            google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    # --- End Workaround ---

    # 4. Build and Save DB Object
    db_search = WeatherSearch(
        location_name=validated_location_name,
        search_date_from=request.search_date_from,
        search_date_to=request.search_date_to,
        **summary_data,
        raw_forecast_data=filtered_raw_data,
        user_note=None,
        google_maps_url=google_maps_url,
        youtube_video_ids=youtube_video_ids,
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

        # 3.5. Fetch External API Data (Task 2.2)
        youtube_video_ids = await get_youtube_videos(validated_location_name)

        # --- Google Maps Workaround (No API Key Needed) ---
        google_maps_url = None
        location_data = raw_api_data.get("location")
        if location_data:
            lat = location_data.get("lat")
            lon = location_data.get("lon")
            if lat and lon:
                google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        # --- End Workaround ---

        # --- Update all data fields (non-user-note) ---
        db_search.location_name = validated_location_name
        db_search.search_date_from = new_date_from
        db_search.search_date_to = new_date_to
        db_search.raw_forecast_data = filtered_raw_data
        db_search.google_maps_url = google_maps_url
        db_search.youtube_video_ids = youtube_video_ids

        for key, value in summary_data.items():
            setattr(db_search, key, value)

    # Update user_note separately (can be done with or without refresh)
    if update_data.user_note is not None:
        db_search.user_note = update_data.user_note

    return update_db_record(db, db_search)


def _convert_search_to_dict(search: WeatherSearch) -> Dict[str, Any]:
    """
    Helper to convert the ORM model to a flat, serializable dict for export.
    We explicitly omit the raw_forecast_data for CSV clarity.
    """
    return {
        "id": search.id,
        "location_name": search.location_name,
        "search_date_from": search.search_date_from.isoformat(),
        "search_date_to": search.search_date_to.isoformat(),
        "summary_avg_temp_c": search.summary_avg_temp_c,
        "summary_condition_text": search.summary_condition_text,
        "summary_avg_humidity": search.summary_avg_humidity,
        "summary_max_wind_kph": search.summary_max_wind_kph,
        "user_note": search.user_note,
        "google_maps_url": search.google_maps_url,
        # Note: Omitting youtube_video_ids for CSV clarity
        "created_at": search.created_at.isoformat(),
    }


async def export_searches(db: Session, format: str) -> Any:
    """
    Orchestrates the export of all search data in the specified format.
    """

    # 1. Get all data from the database
    all_searches = get_all_searches_unpaginated(db)

    if not all_searches:
        if format == "json":
            return []
        else:  # csv
            return ""  # Return an empty string for an empty CSV

    # 2. Convert all ORM objects to plain dicts
    data_as_dicts = [_convert_search_to_dict(search) for search in all_searches]

    # 3. Handle JSON export
    if format == "json":
        # For JSON, we can include the raw data if needed, but for consistency
        # with the CSV, we'll return the flattened dicts.
        return data_as_dicts

    # 4. Handle CSV export
    if format == "csv":
        # Use StringIO to create the CSV in memory
        output = io.StringIO()

        # Use the keys from the first dict as header
        headers = data_as_dicts[0].keys()
        writer = csv.DictWriter(output, fieldnames=headers)

        writer.writeheader()
        writer.writerows(data_as_dicts)

        # Return the string value of the in-memory file
        return output.getvalue()

    # 5. This check is redundant if using Literal in the endpoint,
    # but good for service-level defense.
    raise HTTPException(
        status_code=400,
        detail=f"Invalid export format '{format}'. Supported formats: 'json', 'csv'.",
    )
