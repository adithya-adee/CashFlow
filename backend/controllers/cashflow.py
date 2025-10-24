from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..models import CashFlow as CashFlowModel
from ..schema import CashFlow, CashFlowCreate
from ..database import get_db


router = APIRouter(prefix="/cashflow", tags=["cashflow"])


@router.post("/add", response_model=CashFlow, status_code=status.HTTP_201_CREATED)
def create_cashflow(body: CashFlowCreate, db: Session = Depends(get_db)) -> CashFlow:
    """
    Create a cashflow transaction

    Raises:
        422: If validation fails (amount <= 0)
        400: If database integrity error occurs
    """
    try:
        db_cashflow = CashFlowModel(
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


@router.get("/list", response_model=list[CashFlow], status_code=status.HTTP_200_OK)
def list_cashflows(
    category: str | None = Query(None, description="Filter by category"),
    txn_type: str | None = Query(None, description="Filter by transaction type"),
    account_id: int | None = Query(None, description="Filter by account ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> list[CashFlowModel]:
    """
    Retrieve all cashflow transactions with pagination and filters

    Args:
        category: Optional category filter
        txn_type: Optional transaction type filter (credit/debit)
        account_id: Optional account ID filter
        skip: Number of records to skip (must be >= 0)
        limit: Maximum records to return (must be between 1 and 1000)
    """
    filters = []

    if txn_type is not None:
        filters.append(CashFlowModel.txn_type == txn_type)

    if category is not None:
        filters.append(CashFlowModel.category == category)

    if account_id is not None:
        filters.append(CashFlowModel.account_id == account_id)

    cash_flows = (
        db.query(CashFlowModel).filter(and_(*filters)).offset(skip).limit(limit).all()
    )
    return cash_flows


@router.get("/{cashflow_id}", response_model=CashFlow, status_code=status.HTTP_200_OK)
def get_cashflow_by_id(
    cashflow_id: int, db: Session = Depends(get_db)
) -> CashFlowModel:
    """
    Retrieve a single cashflow transaction by its ID

    Args:
        cashflow_id: The ID of the cashflow transaction

    Raises:
        404: If cashflow not found
    """
    cashflow = db.query(CashFlowModel).filter(CashFlowModel.id == cashflow_id).first()
    if cashflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CashFlow with ID {cashflow_id} not found",
        )
    return cashflow
