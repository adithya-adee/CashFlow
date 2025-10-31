"""
FastAPI application for CashFlow management.
Provides RESTful API endpoints for managing bank accounts and cash flows.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, async_engine
from controllers import account_router, cashflow_router, dashboard_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database tables on startup
# models.account.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CashFlow API is starting up!")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("CashFlow API is shutting down!")


app = FastAPI(
    title="CashFlow API",
    description="API for managing bank accounts and cash flow tracking",
    version="1.0.0",
)

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Account Routes
app.include_router(account_router)

# CashFlow Routes
app.include_router(cashflow_router)

# SuperDashboard Routes
app.include_router(dashboard_router)


@app.get("/")
def get_health_check():
    """Health check endpoint"""
    return {"Hello": "World"}
