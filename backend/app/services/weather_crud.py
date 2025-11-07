"""Database interaction layer for WeatherSearch model (CRUD functions)."""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..db.models.weather import WeatherSearch
from ..schemas.weather import WeatherCreate, WeatherUpdate


# Helper function kept here as it's a pure DB read
def get_search_by_id(db: Session, search_id: int) -> Optional[WeatherSearch]:
    """Retrieves a single weather search record by its ID."""
    return db.query(WeatherSearch).filter(WeatherSearch.id == search_id).first()


# READ operation
def get_all_searches(
    db: Session, skip: int = 0, limit: int = 100
) -> List[WeatherSearch]:
    """Retrieves all weather search records, paginated."""
    return (
        db.query(WeatherSearch)
        .order_by(WeatherSearch.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# DELETE operation
def delete_weather_search(db: Session, search_id: int) -> None:
    """Deletes a weather search record by its ID."""
    db_search = get_search_by_id(db, search_id)
    if db_search is None:
        raise HTTPException(status_code=404, detail="Search record not found.")
    db.delete(db_search)
    db.commit()


# CREATE operation (Just the final DB save, the logic happens in weather_service)
def create_db_record(db: Session, db_search: WeatherSearch) -> WeatherSearch:
    """Saves a new WeatherSearch object to the database."""
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    return db_search


# UPDATE operation (The final DB save part)
def update_db_record(db: Session, db_search: WeatherSearch) -> WeatherSearch:
    """Commits changes to an existing database record."""
    db.commit()
    db.refresh(db_search)
    return db_search
