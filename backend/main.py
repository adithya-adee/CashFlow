"""
FastAPI application for CashFlow management.
Provides RESTful API endpoints for managing bank accounts and cash flows.
"""

from fastapi import FastAPI

from backend.controllers import cashflow

from .controllers import account
from . import models
from .database import engine

# Initialize database tables on startup
models.account.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CashFlow API",
    description="API for managing bank accounts and cash flow tracking",
    version="1.0.0",
)

# Account Routes
app.include_router(account.router)

# CashFlow Routes
app.include_router(cashflow.router)


@app.get("/")
def get_health_check():
    """Health check endpoint"""
    return {"Hello": "World"}
