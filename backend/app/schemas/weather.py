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
    """Schema for PUT /weather/{id}. Defines the input for updating a user note."""

    user_note: str


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
    day1_avg_temp_c: float
    day1_condition_summary: str
    humidity_percent: int
    wind_kph: float

    # External Data
    google_maps_url: Optional[str] = None
    # Using List[str] with Optional=None is clear
    youtube_video_ids: Optional[List[str]] = None

    # User Note and Raw Data
    user_note: Optional[str] = None
    # Raw data should ideally be a defined Pydantic model for validation,
    # but Dict[str, Any] is acceptable for complex, external JSON data.
    raw_forecast_data: Dict[str, Any]

    # Pydantic Configuration for ORM compatibility (Aliased as from_attributes=True since v2)
    model_config = ConfigDict(from_attributes=True)


# --- 3. SCHEMA FOR DELETE RESPONSE ---


class DeleteResponse(BaseModel):
    """Standardized response schema for successful DELETE operations."""

    message: str
