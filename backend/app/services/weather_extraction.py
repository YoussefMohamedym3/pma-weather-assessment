"""Data extraction, filtering, and calculation logic for API responses."""

import copy
from datetime import date
from typing import Any, Dict, List

from fastapi import HTTPException


# Helper function kept here as it's a pure calculation
def _extract_summary_data_for_db(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates average/max summary statistics for the *entire* filtered range.
    """

    forecast_day_list = raw_data.get("forecast", {}).get("forecastday", [])

    if not forecast_day_list:
        raise HTTPException(
            status_code=404,
            detail="No forecast data available for the specified dates after filtering.",
        )

    total_avg_temp = 0
    total_avg_humidity = 0
    max_wind_kph = -float("inf")

    # Get condition from the first day
    first_day_condition = forecast_day_list[0].get("day", {}).get("condition", {})
    condition_text = first_day_condition.get("text", "N/A")

    for day_data in forecast_day_list:
        day_details = day_data.get("day", {})
        total_avg_temp += day_details.get("avgtemp_c", 0)
        total_avg_humidity += day_details.get("avghumidity", 0)
        max_wind_kph = max(max_wind_kph, day_details.get("maxwind_kph", 0))

    count = len(forecast_day_list)
    return {
        "summary_avg_temp_c": total_avg_temp / count,
        "summary_condition_text": condition_text,
        "summary_avg_humidity": total_avg_humidity / count,
        "summary_max_wind_kph": max_wind_kph,
    }


def _filter_raw_data_to_range(
    raw_data: Dict[str, Any], date_from: date, date_to: date
) -> Dict[str, Any]:
    """
    Filters the forecastday list in the raw JSON to only include days
    within the user's requested range.
    """
    forecast_days = raw_data.get("forecast", {}).get("forecastday", [])
    filtered_days = []

    for day_data in forecast_days:
        try:
            day_date = date.fromisoformat(day_data.get("date"))
            if date_from <= day_date <= date_to:
                filtered_days.append(day_data)
        except (ValueError, TypeError):
            continue

    # 2. Use deepcopy to prevent mutating the original data
    filtered_raw_data = copy.deepcopy(raw_data)

    # 3. Now it's safe to modify the nested dictionary
    filtered_raw_data["forecast"]["forecastday"] = filtered_days

    return filtered_raw_data
