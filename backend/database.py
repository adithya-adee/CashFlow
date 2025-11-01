"""
Database configuration and session management.
Provides SQLAlchemy engine, session factory, and base class for ORM models.
"""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
import re

# Database connection URL
SQLITE_DB_URL = "sqlite+aiosqlite:///./data/app.db"

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

@event.listens_for(async_engine.sync_engine, "connect")
def _setup_sqlite_regexp(dbapi_connection, connection_record):
    def regexp(pattern, value):
        return re.search(pattern, value) is not None
    dbapi_connection.create_function("REGEXP", 2, regexp)


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
