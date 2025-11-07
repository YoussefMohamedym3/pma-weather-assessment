"""Defines the SQLAlchemy models for the application's database persistence layer."""

from datetime import date, datetime, timezone
from typing import Any, Dict

from sqlalchemy import JSON, Column, Date, DateTime, Float, Integer, String

from ...core.database import Base


class WeatherSearch(Base):
    """
    Defines the database table structure for storing historical weather search results.
    Each record represents a single request/response for a weather forecast range.
    """

    __tablename__ = "weather_searches"

    # --- Primary Key ---
    id = Column(Integer, primary_key=True, index=True)

    # --- Search Parameters (Inputs from the User) ---
    location_name = Column(
        String,
        index=True,
        nullable=False,
        comment="The validated, official location name returned by the API.",
    )
    search_date_from = Column(
        Date, nullable=False, comment="The requested start date for the forecast range."
    )
    search_date_to = Column(
        Date, nullable=False, comment="The requested end date for the forecast range."
    )

    # --- Extracted Key Metrics (Summarizing the *entire* range) ---
    summary_avg_temp_c = Column(
        Float, comment="Average temperature in Celsius for the entire date range."
    )
    summary_condition_text = Column(
        String,
        comment="Textual summary of the main weather condition on the *first* day.",
    )
    summary_avg_humidity = Column(
        Float, comment="Average humidity percentage for the entire date range."
    )
    summary_max_wind_kph = Column(
        Float,
        comment="Maximum wind speed (kph) recorded across the entire date range.",
    )

    # --- External Data (Milestone 3: Stand-Apart API Data) ---
    google_maps_url = Column(
        String, nullable=True, comment="URL for the location on Google Maps."
    )
    youtube_video_ids = Column(
        JSON,
        nullable=True,
        comment="List of related YouTube video IDs as a JSON array.",
    )

    # --- User-Provided Data ---
    user_note = Column(
        String,
        nullable=True,
        comment="A free-text note added by the user (for the UPDATE endpoint).",
    )

    # --- Raw Data Storage (The complete API response) ---
    raw_forecast_data = Column(
        JSON,
        nullable=False,
        comment="The complete, filtered JSON response from the external weather API.",
    )

    # --- Timestamp ---
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Timestamp (in UTC) when the record was created.",
    )

    # __repr__ for better debugging/logging
    def __repr__(self) -> str:
        return (
            f"<WeatherSearch(id={self.id}, location='{self.location_name}', "
            f"date_from='{self.search_date_from}', created_at='{self.created_at}')>"
        )
