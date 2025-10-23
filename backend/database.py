"""
Database configuration and session management.
Provides SQLAlchemy engine, session factory, and base class for ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL
SQLITE_DB_URL = "sqlite:///../app.db"

# Create database engine
# pool_pre_ping ensures connections are alive before using them
engine = create_engine(
    SQLITE_DB_URL,
    connect_args={
        "check_same_thread": False
    },  # Required for SQLite with multiple threads
    pool_pre_ping=True,  # Verify connection health before checkout
)

# Session factory - creates new sessions for each request
SessionLocal = sessionmaker(
    autocommit=False,  # Explicit transaction control (recommended)
    autoflush=False,  # Manual flush control for better performance
    bind=engine,
)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session to FastAPI endpoints.
    Ensures session is properly closed after request completes.

    Usage:
        @app.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
