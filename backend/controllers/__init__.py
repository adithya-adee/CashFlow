from .account import router as account_router
from .cash_flow import router as cashflow_router
from .dashboard import router as dashboard_router

__all__ = ["account_router", "cashflow_router", "dashboard_router"]
