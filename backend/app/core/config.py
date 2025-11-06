"""Manages application configuration settings using Pydantic."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Loads and validates application settings from environment variables.

    Attributes:
        PROJECT_NAME: Name of the project.
        PROJECT_VERSION: Current project version.
        WEATHERAPI_API_KEY: API key for WeatherAPI.
        WEATHERAPI_BASE_URL: Base URL for WeatherAPI.
        DATABASE_URL: Full database connection string.
    """

    # Project Info
    PROJECT_NAME: str
    PROJECT_VERSION: str

    # WeatherAPI Settings
    WEATHERAPI_API_KEY: str
    WEATHERAPI_BASE_URL: str

    # Database Settings
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """
    Provides a cached, singleton instance of the Settings.

    Using @lru_cache ensures the .env file is read only once.

    Returns:
        Settings: The application settings object.
    """
    return Settings()
