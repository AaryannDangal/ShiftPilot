"""Database configuration for ShiftPilot."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

database_url = settings.database_url if hasattr(settings, "database_url") else settings.DATABASE_URL

engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if "sqlite" in str(database_url) else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Yield a database session and ensure cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
