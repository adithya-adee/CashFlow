from sqlite3 import IntegrityError
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from backend import models
from backend.database import get_db
from backend.schema import CashFlow, CashFlowBase


router = APIRouter()


@router.post("/cashflow/", response_model=CashFlowBase, status_code=status.HTTP_201_CREATED)
def create_cashflow(body: CashFlowBase, db: Session = Depends(get_db)) -> CashFlow:
    """
    Create a cashflow

    Raises:
    400 if amount <= 0
    """

    # Validate amount is positive
    if body.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0",
        )

    try:
        db_cashflow = models.cash_flow.CashFlow(
            account_id=body.account_id,
            amount=body.amount,
            description=body.description,
            txn_type=body.txn_type,
            category=body.category,
        )
        db.add(db_cashflow)
        db.commit()
        db.refresh(db_cashflow)
        return db_cashflow
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred",
        )


@router.get("/cashflow/", response_model=list[CashFlow], status_code=status.HTTP_200_OK)
def get_all_cashflow(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[models.cash_flow.CashFlow]:
    """
    Retrieve all cashflow with pagination

    Skip must be greateer than 0
    Limit must be between 1 & 1000
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter cannot be negative",
        )

    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 1000",
        )
    cash_flows = db.query(models.cash_flow.CashFlow).limit(limit).offset(skip).all()
    return cash_flows
