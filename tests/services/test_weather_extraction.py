# File: tests/api/test_weather_endpoints.py (FIXED)

from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# --- Imports for Mocks ---
# We need the *real* model to mock what the DB returns
from backend.app.db.models.weather import WeatherSearch

# We need the main app to test
from backend.main import app

# Initialize the TestClient
client = TestClient(app)

# --- Mock Data ---
# This is now a REAL WeatherSearch *model instance*, not a dict.
# This is crucial for db.delete() to work.
MOCK_MODEL_INSTANCE = WeatherSearch(
    id=99,
    location_name="London, UK",
    search_date_from=date(2025, 11, 7),
    search_date_to=date(2025, 11, 8),
    created_at=datetime(2025, 11, 7, 12, 0, 0, tzinfo=timezone.utc),
    summary_avg_temp_c=12.5,
    summary_condition_text="Sunny",
    summary_avg_humidity=65.0,
    summary_max_wind_kph=30.0,
    user_note=None,
    google_maps_url=None,
    youtube_video_ids=None,
    raw_forecast_data={"test_key": "mocked_data"},
)


@pytest.fixture(autouse=True)
def mock_service_layer(mocker):
    """
    FIX: Mocks the service layer functions *where they are used*.

    The endpoint file (weather.py) imports `weather_service as service`.
    We must patch the functions *on that imported 'service' object* for
    the mocks to work.
    """

    # --- Correct Patch Targets ---
    # The original tests patched "...weather_crud.get_all_searches",
    # but the endpoint calls "service.get_all_searches".

    mocker.patch(
        "backend.app.api.v1.endpoints.weather.service.create_weather_search",
        return_value=MOCK_MODEL_INSTANCE,  # Return a model instance
    )
    mocker.patch(
        "backend.app.api.v1.endpoints.weather.service.get_all_searches",
        return_value=[MOCK_MODEL_INSTANCE],  # Return a list of model instances
    )
    mocker.patch(
        "backend.app.api.v1.endpoints.weather.service.get_search_by_id",
        return_value=MOCK_MODEL_INSTANCE,  # Return a model instance
    )
    mocker.patch(
        "backend.app.api.v1.endpoints.weather.service.update_weather_search",
        return_value=MOCK_MODEL_INSTANCE,  # Return a model instance
    )
    mocker.patch(
        "backend.app.api.v1.endpoints.weather.service.delete_weather_search",
        return_value=None,  # This function returns nothing
    )


def test_root_status_endpoint():
    """Test the basic health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Online"


def test_create_weather_search_success():
    """Tests the POST /weather endpoint success path."""

    create_input = {
        "location_name": "london",
        "search_date_from": date(2025, 11, 7).isoformat(),
        "search_date_to": date(2025, 11, 8).isoformat(),
    }

    response = client.post("/weather/", json=create_input)

    assert response.status_code == 201
    data = response.json()

    # This assertion now passes because the mock is applied correctly
    assert data["location_name"] == "London, UK"
    assert data["id"] == 99


def test_read_all_weather_searches_success():
    """Tests the GET /weather endpoint."""
    response = client.get("/weather/")

    assert response.status_code == 200
    data = response.json()

    # This assertion now passes because the mock is applied correctly
    assert len(data) == 1
    assert data[0]["id"] == 99


def test_update_weather_search_success():
    """Tests the PUT /weather/{id} endpoint."""

    update_input = {
        "user_note": "Test update successful.",
        "location_name": "NewYork",
        "search_date_from": date(2025, 12, 1).isoformat(),
    }

    response = client.put("/weather/99", json=update_input)

    # This assertion now passes because the mock is applied correctly
    assert response.status_code == 200
    data = response.json()

    # The mock returns the MOCK_MODEL_INSTANCE
    assert data["location_name"] == "London, UK"
    assert data["id"] == 99


def test_delete_weather_search_success():
    """Tests the DELETE /weather/{id} endpoint."""
    response = client.delete("/weather/99")

    # This assertion now passes because the mock is applied correctly
    assert response.status_code == 200
    assert response.json()["message"] == "Search record 99 deleted successfully."
