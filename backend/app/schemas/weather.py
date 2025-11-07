"""Defines the Pydantic schemas for API request and response validation."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

# --- 1. SCHEMAS FOR API INPUT (Write Operations) ---


class WeatherCreate(BaseModel):
    """Schema for POST /weather. Defines the required input for a new weather search."""

    location_name: str
    search_date_from: date
    search_date_to: date


class WeatherUpdate(BaseModel):
    """
    Schema for PUT /weather/{id}. Defines optional fields for updating a search.
    Updating location or dates will trigger a full API data refresh.
    """

    location_name: Optional[str] = None
    search_date_from: Optional[date] = None
    search_date_to: Optional[date] = None
    user_note: Optional[str] = None

    # Ensure at least one field is provided for an update
    @classmethod
    def model_validate(cls, data: Any, *args, **kwargs) -> "WeatherUpdate":
        if isinstance(data, dict) and all(v is None for v in data.values()):
            raise ValueError("At least one field must be provided for update.")
        return super().model_validate(data, *args, **kwargs)


# --- 2. SCHEMAS FOR API OUTPUT (Read/Display Operations) ---


class WeatherDisplay(BaseModel):
    """
    Schema for returning a stored weather search record (the simplified view).
    Used for GET responses.
    """

    id: int

    # Location/Time and Search Parameters
    location_name: str
    search_date_from: date
    search_date_to: date
    created_at: datetime

    # Key Metrics (Matching the SQLAlchemy model)
    summary_avg_temp_c: Optional[float] = None
    summary_condition_text: Optional[str] = None
    summary_avg_humidity: Optional[float] = None
    summary_max_wind_kph: Optional[float] = None

    # External Data
    google_maps_url: Optional[str] = None
    youtube_video_ids: Optional[List[str]] = None

    # User Note and Raw Data
    user_note: Optional[str] = None
    raw_forecast_data: Dict[str, Any]

    # Pydantic Configuration for ORM compatibility
    model_config = ConfigDict(from_attributes=True)


# --- 3. SCHEMA FOR DELETE RESPONSE ---


class DeleteResponse(BaseModel):
    """Standardized response schema for successful DELETE operations."""

    message: str
