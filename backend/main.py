"""The primary entry point for the FastAPI application."""

import logging

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# --- Project Imports ---
from .app.api.v1.endpoints import weather
from .app.core.config import settings
from .app.core.database import Base, engine  # Imports Base class and DB engine
from .app.db.models import (
    weather as weather_model_import,  # Ensures the model definition is loaded
)

# --- Initialization Functions ---
# Basic configuration to output logs to the console
logging.basicConfig(level=logging.INFO)
# Note: You can change level=INFO to level=DEBUG during heavy development


def create_db_tables():
    """Initializes the database by creating all tables defined in Base."""
    # We explicitly import the model definition above to ensure SQLAlchemy knows
    # about the WeatherSearch class before calling create_all().
    Base.metadata.create_all(bind=engine)


# --- Application Startup ---

# NOTE ON DATABASE SETUP:
# Base.metadata.create_all(bind=engine) is used here for simple demonstration
# and easy setup. In a production environment, this would be replaced by
# a dedicated database migration tool (Alembic) to safely manage schema changes
# without losing data during upgrades.
create_db_tables()


# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Backend API for Weather Assessment featuring full CRUD, validation, and decoupled services.",
)

# --- Include Routers ---

# The weather router contains all our CRUD endpoints
app.include_router(weather.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Basic Health Check ---


@app.get("/", tags=["Status"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "Online",
        "database_url": settings.DATABASE_URL,
    }
