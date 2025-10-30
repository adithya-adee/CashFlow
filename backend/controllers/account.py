import os
import logging
from typing import Sequence
from sqlalchemy import delete, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..schema import AccountCreate, Account, AccountEdit
from ..models import Account as AccountModel, CashFlow as CashFlowModel
from ..database import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)

DEBUG = os.getenv("DEBUG", "False") == "True"


@router.post("/add", response_model=Account, status_code=status.HTTP_201_CREATED)
async def create_account(
    body: AccountCreate, db: AsyncSession = Depends(get_db)
) -> Account:
    """
    Create a new bank account.

    Creates a new bank account after validating that the account number is unique.

    Args:
        body: Account details including bank_account_no, bank_name, holder_name,
              account_type, balance, and currency.
        db: Database session dependency.

    Returns:
        The newly created account with auto-generated ID and timestamps.

    Raises:
        HTTPException:
            - 400: Account number already exists or integrity constraint violation.
            - 500: Database or unexpected server error.
    """
    try:
        # Check for duplicate account number
        result = await db.execute(
            select(AccountModel).where(
                AccountModel.bank_account_no == body.bank_account_no
            )
        )
        existing_account = result.scalar_one_or_none()

        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account number already exists",
            )

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
        await db.commit()
        await db.refresh(db_account)

        return db_account

    except IntegrityError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Integrity error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity constraint violated. Please check your input.",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"SQLAlchemy error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating account.",
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Unexpected error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.get("/list", response_model=list[Account], status_code=status.HTTP_200_OK)
async def list_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
) -> Sequence[AccountModel]:
    """
    Retrieve a paginated list of all bank accounts.

    Supports pagination through skip and limit parameters for efficient data retrieval.

    Args:
        skip: Number of records to skip (offset). Must be >= 0.
        limit: Maximum number of records to return. Must be between 1 and 1000.
        db: Database session dependency.

    Returns:
        List of account objects, or empty list if no accounts exist.

    Raises:
        HTTPException:
            - 500: Database error during retrieval.
    """
    try:
        result = await db.execute(
            select(AccountModel)
            .order_by(AccountModel.id.desc())
            .offset(skip)
            .limit(limit)
        )
        accounts = result.scalars().all()

        return accounts if accounts else []

    except SQLAlchemyError as e:
        if DEBUG:
            logger.error(f"SQLAlchemy error retrieving accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving accounts from database.",
        )


@router.get("/{account_id}", response_model=Account, status_code=status.HTTP_200_OK)
async def get_account_by_id(
    account_id: int, db: AsyncSession = Depends(get_db)
) -> AccountModel:
    """
    Retrieve a specific bank account by ID.

    Args:
        account_id: Unique identifier of the account.
        db: Database session dependency.

    Returns:
        Account object matching the provided ID.

    Raises:
        HTTPException:
            - 404: Account not found.
            - 500: Database error during retrieval.
    """
    try:
        result = await db.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        account = result.scalar_one_or_none()

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )

        return account

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        if DEBUG:
            logger.error(f"SQLAlchemy error retrieving account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving account from database.",
        )


@router.patch("/{account_id}", response_model=Account, status_code=status.HTTP_200_OK)
async def edit_account_by_id(
    account_id: int, body: AccountEdit, db: AsyncSession = Depends(get_db)
) -> Account:
    """
    Update an existing bank account.

    Performs partial updates - only fields provided in the request body are updated.
    Validates account existence and checks for duplicate account numbers if changed.

    Args:
        account_id: Unique identifier of the account to update.
        body: Fields to update (all optional).
        db: Database session dependency.

    Returns:
        Updated account object.

    Raises:
        HTTPException:
            - 404: Account not found.
            - 400: Duplicate account number or integrity constraint violation.
            - 500: Database error during update.
    """
    try:
        # Fetch existing account
        result = await db.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()

        if db_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )

        # Check for duplicate account number if being changed and exclude the current account_id
        if (
            body.bank_account_no is not None
            and body.bank_account_no != db_account.bank_account_no
        ):
            duplicate_check = await db.execute(
                select(AccountModel).where(
                    AccountModel.bank_account_no == body.bank_account_no,
                    AccountModel.id != account_id,
                )
            )
            if duplicate_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account number already exists",
                )

        # Build update dictionary with only changed fields
        update_data = body.model_dump(exclude_unset=True)

        if not update_data:
            # No fields to update, return existing account
            return db_account

        # Perform update
        stmt = (
            update(AccountModel)
            .where(AccountModel.id == account_id)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(db_account)

        return db_account

    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Integrity error updating account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity constraint violated. Ensure all values are valid.",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"SQLAlchemy error updating account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating account in database.",
        )


@router.delete("/{account_id}", status_code=status.HTTP_200_OK)
async def delete_account_by_id(
    account_id: int, db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Delete a bank account and all associated cash flow records.

    This is a cascading delete operation that removes both the account and
    all related cash flow transactions.

    Args:
        account_id: Unique identifier of the account to delete.
        db: Database session dependency.

    Returns:
        Success message with count of deleted cash flow records.

    Raises:
        HTTPException:
            - 404: Account not found.
            - 400: Database integrity constraint violation.
            - 500: Database error during deletion.
    """
    try:
        # Verify account exists
        result = await db.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()

        if db_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )

        # Count and delete related cash flows
        cashflow_count_result = await db.execute(
            select(func.count(CashFlowModel.id)).where(
                CashFlowModel.account_id == account_id
            )
        )
        cashflow_count = cashflow_count_result.scalar()

        await db.execute(
            delete(CashFlowModel).where(CashFlowModel.account_id == account_id)
        )

        # Delete the account
        await db.execute(delete(AccountModel).where(AccountModel.id == account_id))
        await db.commit()

        return {
            "message": "Account deleted successfully",
            "account_id": account_id,
            "cashflows_deleted": cashflow_count,
        }

    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Integrity error deleting account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete account due to database constraints.",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"SQLAlchemy error deleting account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting account from database.",
        )
