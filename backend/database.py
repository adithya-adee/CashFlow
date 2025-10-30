"""
Database configuration and session management.
Provides SQLAlchemy engine, session factory, and base class for ORM models.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

# Database connection URL
SQLITE_DB_URL = "sqlite+aiosqlite:///../app.db"

# Create database engine
# pool_pre_ping ensures connections are alive before using them
async_engine = create_async_engine(
    SQLITE_DB_URL,
    connect_args={
        "check_same_thread": False
    },  # Required for SQLite with multiple threads
    pool_pre_ping=True,  # Verify connection health before checkout
)

# Session factory - creates new sessions for each request
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for all ORM models
Base = declarative_base()


async def get_db():
    """
    Dependency that provides a database session to FastAPI endpoints.
    Ensures session is properly closed after request completes.

    Usage:
        @app.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    async with AsyncSessionLocal() as session:
        yield session
