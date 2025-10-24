from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.schema import AccountCreate
from ..database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from .. import models

router = APIRouter()


@router.post("/accounts/", status_code=status.HTTP_201_CREATED)
def create_account(body: AccountCreate, db: Session = Depends(get_db)):
    """
        Create a new bank account.

        Returns:
            The created account with auto-generated ID and timestamp
    Raises: 400: If account number already exists or validation fails
    """
    # Check if account number already exists
    existing_account = (
        db.query(models.account.Account)
        .filter(models.account.Account.bank_account_no == body.bank_account_no)
        .first()
    )

    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account number '{body.bank_account_no}' already exists",
        )

    # Validate balance is non-negative
    if body.balance < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Balance cannot be negative"
        )

    try:
        # Create new account
        db_account = models.account.Account(
            bank_account_no=body.bank_account_no,
            bank_name=body.bank_name,
            holder_name=body.holder_name,
            account_type=body.account_type,
            balance=body.balance,
            currency=body.currency,
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred",
        )


@router.get("/accounts/")
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve list of accounts with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of accounts
    """
    # Validate pagination parameters
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

    accounts = db.query(models.account.Account).offset(skip).limit(limit).all()
    return accounts
