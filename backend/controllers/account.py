from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..schema import AccountCreate, Account
from ..models import Account as AccountModel
from ..database import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(body: AccountCreate, db: Session = Depends(get_db)) -> Account:
    """
    Create a new bank account.

    Returns:
        The created account with auto-generated ID and timestamp

    Raises:
        400: If account number already exists or validation fails
    """
    # Check if account number already exists
    existing_account = (
        db.query(AccountModel)
        .filter(AccountModel.bank_account_no == body.bank_account_no)
        .first()
    )

    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account number '{body.bank_account_no}' already exists",
        )

    try:
        # Create new account
        db_account = AccountModel(
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


@router.get("/", response_model=list[Account], status_code=status.HTTP_200_OK)
def list_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> list[AccountModel]:
    """
    Retrieve list of accounts with pagination.

    Args:
        skip: Number of records to skip (default: 0, must be >= 0)
        limit: Maximum number of records to return (default: 100, must be 1-1000)

    Returns:
        List of accounts
    """
    accounts = db.query(AccountModel).offset(skip).limit(limit).all()
    return accounts


@router.get("/{account_id}", response_model=Account, status_code=status.HTTP_200_OK)
def get_account_by_id(account_id: int, db: Session = Depends(get_db)) -> AccountModel:
    """
    Retrieve a single account by its ID

    Args:
        account_id: The ID of the account

    Raises:
        404: If account not found
    """
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )
    return account
