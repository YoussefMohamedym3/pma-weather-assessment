from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException

from backend.app.core.config import settings

# --- Private Helper Function: Network Caller  ---


async def _fetch_from_weatherapi(
    endpoint: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generic, private helper function to call the WeatherAPI.com endpoints.
    """
    if not settings.WEATHERAPI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: WeatherAPI key is missing.",
        )

    params["key"] = settings.WEATHERAPI_API_KEY
    base_url = f"{settings.WEATHERAPI_BASE_URL}/{endpoint}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            error_msg = data["error"].get("message", "Unknown API error.")
            status_code = data["error"].get("code", 400)

            # 1006 is "No location found matching parameter 'q'"
            if status_code == 1006:
                raise HTTPException(
                    status_code=404, detail=f"Location not found: {error_msg}"
                )

            raise HTTPException(
                status_code=400, detail=f"Weather API Error: {error_msg}"
            )

        return data

    except httpx.HTTPStatusError as e:
        detail_msg = f"External weather service error: {e.response.reason_phrase} - {e.response.text}"
        raise HTTPException(status_code=e.response.status_code, detail=detail_msg)

    except httpx.RequestException as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to connect to weather service: {e}"
        )


# --- Public Function: Location Validation  ---


async def validate_location_exists(location: str) -> str:
    """
    Uses the /search.json endpoint to validate a location and handle fuzzy matching.
    Returns the official name of the top-matched location.
    Raises 404 if no location is found.
    """
    params = {"q": location}
    try:
        # The search API returns a LIST of matches, not a single dict
        data = await _fetch_from_weatherapi("search.json", params)

        if not isinstance(data, list) or not data:
            raise HTTPException(
                status_code=404,
                detail=f"Location not found or ambiguous: '{location}'.",
            )

        # Success: Return the name of the first (best) match
        return data[0].get("name", location)

    except HTTPException as e:
        # Re-raise 404s with a clearer message
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Location not found for query: '{location}'.",
            )
        raise e


# --- Public Function: Data Retrieval Orchestrator ---


async def get_raw_weather_data_for_range(
    location: str, date_from: date, date_to: date
) -> Dict[str, Any]:
    """
    Fetches raw weather data, handling multi-day historical requests
    by looping over history.json calls.
    """
    today = datetime.now(timezone.utc).date()

    # Check 1: CURRENT/FUTURE FORECAST DATA (EASY PATH: single API call)
    # We now use the validated location name passed to this function.
    if date_from >= today:
        params = {"q": location, "days": 14, "aqi": "yes", "alerts": "yes"}
        raw_data = await _fetch_from_weatherapi("forecast.json", params)

    # Check 2: HISTORICAL DATA (HARD PATH: requires looping)
    elif date_from < today:
        min_history_date = date(2010, 1, 1)
        if date_from < min_history_date:
            raise HTTPException(
                status_code=400,
                detail=f"Historical data is only available from {min_history_date.isoformat()}.",
            )

        historical_days = []
        current_date = date_from
        last_day_data = {}  # To store the response for location data

        while current_date <= date_to:
            params = {"q": location, "dt": current_date.isoformat(), "aqi": "yes"}
            day_data = await _fetch_from_weatherapi("history.json", params)
            last_day_data = day_data  # Save the last successful fetch

            forecast_day_list = day_data.get("forecast", {}).get("forecastday", [])
            if forecast_day_list:
                historical_days.append(forecast_day_list[0])

            current_date += timedelta(days=1)

        if not last_day_data:
            raise HTTPException(
                status_code=404, detail="No historical data found for range."
            )

        # Stitch results into a consistent structure
        raw_data = {
            "location": last_day_data.get("location", {}),
            "forecast": {"forecastday": historical_days},
        }

    else:
        raise HTTPException(
            status_code=500, detail="Internal server error resolving date range type."
        )

    if not raw_data:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve weather data for the specified range.",
        )

    return raw_data
