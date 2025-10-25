from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status, Query
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


from ..schema import AccountCreate, Account, AccountEdit
from ..models import Account as AccountModel, CashFlow as CashFlowModel
from ..database import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/add", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(body: AccountCreate, db: Session = Depends(get_db)) -> Account:
    """
    Create a new bank account.

    This endpoint allows the creation of a new bank account with the provided details.
    It performs a check to ensure no account with the same bank account number already exists.

    Args:
        body (AccountCreate): The request body containing account details.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Account: The newly created account with auto-generated ID and timestamps.

    Raises:
        HTTPException:
            - 400 Bad Request: If an account with the provided bank account number
            already exists, or if a database integrity error occurs.
            - 422 Unprocessable Entity: If request body validation fails.
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


@router.get("/list", response_model=list[Account], status_code=status.HTTP_200_OK)
def list_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> list[AccountModel]:
    """
    Retrieve a paginated list of accounts.

    This endpoint fetches all bank accounts, allowing for pagination to control
    the number of records returned and the starting offset.

    Args:
        skip (int, optional): The number of records to skip. Must be non-negative.
                            Defaults to 0.
        limit (int, optional): The maximum number of records to return. Must be
                            between 1 and 1000. Defaults to 100.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        list[Account]: A list of account objects.

    Raises:
        HTTPException:
            - 422 Unprocessable Entity: If query parameters fail validation
            (e.g., `skip` is negative, `limit` is out of range).
    """
    accounts = db.query(AccountModel).offset(skip).limit(limit).all()
    return accounts


@router.get("/{account_id}", response_model=Account, status_code=status.HTTP_200_OK)
def get_account_by_id(account_id: int, db: Session = Depends(get_db)) -> AccountModel:
    """
    Retrieve a single account by its ID.

    This endpoint fetches the details of a specific bank account using its unique ID.

    Args:
        account_id (int): The unique identifier of the account to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Account: The account object matching the provided ID.

    Raises:
        HTTPException:
            - 404 Not Found: If no account with the given `account_id` is found.
            - 422 Unprocessable Entity: If `account_id` is not a valid integer.
    """
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )
    return account


@router.patch("/{account_id}", response_model=Account, status_code=HTTP_200_OK)
def edit_account_by_id(
    account_id: int, body: AccountEdit, db: Session = Depends(get_db)
) -> Account:
    """
    Edit an existing account by ID.

    This endpoint allows partial updates to an existing bank account. Only the fields
    provided in the request body will be updated.

    Args:
        account_id (int): The unique identifier of the account to update.
        body (AccountEdit): The request body containing the fields to update.
                            All fields are optional.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Account: The updated account object.

    Raises:
        HTTPException:
            - 404 Not Found: If no account with the given `account_id` is found.
            - 400 Bad Request: If a database integrity error occurs (e.g.,
            attempting to use an existing `bank_account_no`).
            - 422 Unprocessable Entity: If request body or path parameters fail validation.
    """
    try:
        db_account = (
            db.query(AccountModel).filter(AccountModel.id == account_id).first()
        )

        if db_account is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Account not found"
            )

        update_values = {}

        if (
            body.bank_account_no is not None
            and body.bank_account_no != db_account.bank_account_no
        ):
            update_values["bank_account_no"] = body.bank_account_no

        if body.bank_name is not None and body.bank_name != db_account.bank_name:
            update_values["bank_name"] = body.bank_name

        if (
            body.account_type is not None
            and body.account_type != db_account.account_type
        ):
            update_values["account_type"] = body.account_type

        if body.holder_name is not None and body.holder_name != db_account.holder_name:
            update_values["holder_name"] = body.holder_name

        if body.balance is not None and body.balance != db_account.balance:
            update_values["balance"] = body.balance

        if body.currency is not None and body.currency != db_account.currency:
            update_values["currency"] = body.currency

        if update_values:
            stmt = (
                update(AccountModel)
                .where(AccountModel.id == account_id)
                .values(**update_values)
            )
            db.execute(stmt)
            db.commit()
            db.refresh(db_account)

        return db_account

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Database integrity error occurred"
        )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account_by_id(account_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete an account by ID.

    This endpoint deletes a bank account and all associated cashflow transactions.

    Args:
        account_id (int): The unique identifier of the account to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        None: No content is returned upon successful deletion (204 No Content).

    Raises:
        HTTPException:
            - 404 Not Found: If no account with the given `account_id` is found.
            - 400 Bad Request: If a database integrity error occurs during deletion.
            - 422 Unprocessable Entity: If `account_id` is not a valid integer.
    """
    try:
        # Check if account exists
        db_account = (
            db.query(AccountModel).filter(AccountModel.id == account_id).first()
        )
        if db_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )

        # Delete related cashflows first
        db.query(CashFlowModel).filter(CashFlowModel.account_id == account_id).delete()
        db.delete(db_account)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred",
        )
