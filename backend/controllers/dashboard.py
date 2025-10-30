import os
import logging
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from schema import TransactionType
from models import Account as AccountModel, CashFlow as CashFlowModel
from schema.dashboard import SuperDashboardQuery
from database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

DEBUG = os.getenv("DEBUG", "False") == "True"


@router.post("/super", response_model=dict, status_code=status.HTTP_200_OK)
async def super_dashboard(
    body: SuperDashboardQuery, db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Retrieve comprehensive dashboard statistics.

    Fetches total accounts, total cashflows, total balance sum, and credit/debit breakdown.
    """
    try:
        result = await db.execute(
            select(
                func.count(AccountModel.id).label("total_accounts"),
                func.sum(AccountModel.balance).label("total_balance"),
            )
        )
        accounts_data = result.one()

        result = await db.execute(
            select(
                func.count(CashFlowModel.id).label("total_cashflows"),
                func.count(CashFlowModel.txn_type)
                .filter(CashFlowModel.txn_type == TransactionType.debit)
                .label("total_debit_count"),
                func.count(CashFlowModel.txn_type)
                .filter(CashFlowModel.txn_type == TransactionType.credit)
                .label("total_credit_count"),
                func.sum(CashFlowModel.amount)
                .filter(CashFlowModel.txn_type == TransactionType.credit)
                .label("total_credits"),
                func.sum(CashFlowModel.amount)
                .filter(CashFlowModel.txn_type == TransactionType.debit)
                .label("total_debits"),
            )
        )
        cashflow_data = result.one()

        total_accounts = accounts_data.total_accounts or 0
        total_balance = float(accounts_data.total_balance or 0.0)
        total_cashflows = cashflow_data.total_cashflows or 0
        total_credits_count = cashflow_data.total_credit_count or 0
        total_debits_count = cashflow_data.total_debit_count or 0
        total_credits = float(cashflow_data.total_credits or 0.0)
        total_debits = float(cashflow_data.total_debits or 0.0)

        return {
            "total_counts": {
                "total_accounts": total_accounts,
                "total_cashflows": total_cashflows,
                "total_credits_count": total_credits_count,
                "total_debits_count": total_debits_count,
            },
            "balance_summary": {
                "total_balance": total_balance,
                "total_credits": total_credits,
                "total_debits": total_debits,
            },
        }

    except SQLAlchemyError as e:
        if DEBUG:
            logger.error(f"SQLAlchemy error fetching dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching dashboard data.",
        )
    except Exception as e:
        if DEBUG:
            logger.error(f"Unexpected error fetching dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
