import os
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_, delete, select,  update
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.sql import func

from models import CashFlow as CashFlowModel, Account as AccountModel
from schema import CashFlow, CashFlowCreate, CashFlowEdit, TransactionType,CashFlowWithAccountDetails
from database import get_db

router = APIRouter(prefix="/cashflow", tags=["cashflow"])
logger = logging.getLogger(__name__)

DEBUG = os.getenv("DEBUG", "False") == "True"


@router.post("/add", response_model=CashFlow, status_code=status.HTTP_201_CREATED)
async def create_cashflow(
    body: CashFlowCreate, db: AsyncSession = Depends(get_db)
) -> CashFlow:
    """
    Create a new cashflow transaction and update associated account balance.
    """
    try:
        result = await db.execute(
            select(AccountModel).where(AccountModel.id == body.account_id)
        )
        db_account = result.scalar_one_or_none()

        if db_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        db_cashflow = CashFlowModel(
            account_id=body.account_id,
            amount=body.amount,
            description=body.description,
            txn_type=body.txn_type,
            category=body.category,
        )
        db.add(db_cashflow)

        new_balance = 0
        match db_cashflow.txn_type:
            case TransactionType.credit:
                new_balance = db_account.balance + db_cashflow.amount
            case TransactionType.debit:
                new_balance = db_account.balance - db_cashflow.amount

        stmt = (
            update(AccountModel)
            .where(AccountModel.id == db_cashflow.account_id)
            .values(balance=new_balance)
        )
        await db.execute(stmt)

        await db.commit()
        await db.refresh(db_cashflow)
        return db_cashflow

    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Integrity error creating cashflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred.",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"SQLAlchemy error creating cashflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating cashflow.",
        )
    except Exception as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Unexpected error creating cashflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.get("/list", response_model=dict, status_code=status.HTTP_200_OK)
async def list_cashflows(
    account_no_regex: str | None = Query(None, description="Filter by account number"),
    category: str | None = Query(None, description="Filter by category"),
    txn_type: str | None = Query(None, description="Filter by transaction type"),
    account_id: int | None = Query(None, description="Filter by account ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Retrieve paginated cashflow transactions with optional filters.
    """
    try:
        filters = []

        if txn_type is not None:
            filters.append(CashFlowModel.txn_type == txn_type)

        if category is not None:
            filters.append(CashFlowModel.category == category)

        if account_id is not None:
            filters.append(CashFlowModel.account_id == account_id)

        query = select(
            CashFlowModel,
            AccountModel.bank_account_no,
            AccountModel.currency
        ).join(AccountModel, AccountModel.id == CashFlowModel.account_id)
        count_query = select(func.count(CashFlowModel.id))

        if account_no_regex is not None:
            count_query = count_query.join(AccountModel, AccountModel.id == CashFlowModel.account_id)
            # Use the custom REGEXP operator for SQLite
            filters.append(text(f"Account.bank_account_no REGEXP '{account_no_regex}'"))

        if filters:
            query = query.filter(and_(*filters))
            count_query = count_query.filter(and_(*filters))

        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar_one_or_none() or 0

        result = await db.execute(
            query.offset(skip).limit(limit).order_by(CashFlowModel.created_at.desc())
        )
        cash_flows_with_account_details = []
        for cf_model, bank_account_no, currency in result.all():
            cash_flows_with_account_details.append(
                CashFlowWithAccountDetails(
                    id=cf_model.id,
                    account_id=cf_model.account_id,
                    txn_type=cf_model.txn_type,
                    amount=cf_model.amount,
                    category=cf_model.category,
                    description=cf_model.description,
                    created_at=cf_model.created_at,
                    updated_at=cf_model.updated_at,
                    bank_account_no=bank_account_no,
                    currency=currency,
                )
            )

        page_number = (skip // limit) + 1 if limit > 0 else 1

        return {
            "data": cash_flows_with_account_details,
            "page_size": limit,
            "page_number": page_number,
            "total_count": total_count,
        }

    except SQLAlchemyError as e:
        if DEBUG:
            logger.error(f"SQLAlchemy error retrieving cashflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving cashflows from database.",
        )


@router.get("/{cashflow_id}", response_model=CashFlow, status_code=status.HTTP_200_OK)
async def get_cashflow_by_id(
    cashflow_id: int, db: AsyncSession = Depends(get_db)
) -> CashFlowModel:
    """
    Retrieve a specific cashflow transaction by ID.
    """
    try:
        result = await db.execute(
            select(CashFlowModel).where(CashFlowModel.id == cashflow_id)
        )
        cashflow = result.scalar_one_or_none()

        if cashflow is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CashFlow with ID {cashflow_id} not found",
            )

        return cashflow

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        if DEBUG:
            logger.error(f"SQLAlchemy error retrieving cashflow {cashflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving cashflow from database.",
        )


@router.patch("/{cashflow_id}", response_model=CashFlow, status_code=status.HTTP_200_OK)
async def edit_cashflow_by_id(
    cashflow_id: int, body: CashFlowEdit, db: AsyncSession = Depends(get_db)
) -> CashFlow:
    """
    Update an existing cashflow transaction and adjust account balances accordingly.
    """
    try:
        result = await db.execute(
            select(CashFlowModel).where(CashFlowModel.id == cashflow_id)
        )
        db_cashflow = result.scalar_one_or_none()

        if db_cashflow is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CashFlow with ID {cashflow_id} not found",
            )

        update_values = {}

        if body.category is not None and body.category != db_cashflow.category:
            update_values["category"] = body.category

        if body.description is not None and body.description != db_cashflow.description:
            update_values["description"] = body.description

        if body.txn_type is not None and body.txn_type != db_cashflow.txn_type:
            update_values["txn_type"] = body.txn_type

        if body.amount is not None and body.amount != db_cashflow.amount:
            update_values["amount"] = body.amount

        if body.account_id is not None and body.account_id != db_cashflow.account_id:
            update_values["account_id"] = body.account_id

        final_amount = update_values.get("amount", db_cashflow.amount)
        final_txn_type = update_values.get("txn_type", db_cashflow.txn_type)
        final_account_id = update_values.get("account_id", db_cashflow.account_id)

        if (
            "amount" in update_values
            or "txn_type" in update_values
            or "account_id" in update_values
        ):
            result = await db.execute(
                select(AccountModel).where(AccountModel.id == db_cashflow.account_id)
            )
            old_account = result.scalar_one_or_none()

            if old_account is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Old account not found",
                )

            old_balance_adjustment = 0
            match db_cashflow.txn_type:
                case TransactionType.credit:
                    old_balance_adjustment = -db_cashflow.amount
                case TransactionType.debit:
                    old_balance_adjustment = db_cashflow.amount

            if "account_id" in update_values:
                result = await db.execute(
                    select(AccountModel).where(AccountModel.id == final_account_id)
                )
                new_account = result.scalar_one_or_none()

                if new_account is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="New account not found",
                    )

                updated_old_balance = old_account.balance + old_balance_adjustment
                await db.execute(
                    update(AccountModel)
                    .where(AccountModel.id == old_account.id)
                    .values(balance=updated_old_balance)
                )

                new_balance_adjustment = 0
                match final_txn_type:
                    case TransactionType.credit:
                        new_balance_adjustment = final_amount
                    case TransactionType.debit:
                        new_balance_adjustment = -final_amount

                updated_new_balance = new_account.balance + new_balance_adjustment
                await db.execute(
                    update(AccountModel)
                    .where(AccountModel.id == new_account.id)
                    .values(balance=updated_new_balance)
                )
            else:
                new_balance_adjustment = 0
                match final_txn_type:
                    case TransactionType.credit:
                        new_balance_adjustment = final_amount
                    case TransactionType.debit:
                        new_balance_adjustment = -final_amount

                updated_balance = (
                    old_account.balance
                    + old_balance_adjustment
                    + new_balance_adjustment
                )
                await db.execute(
                    update(AccountModel)
                    .where(AccountModel.id == old_account.id)
                    .values(balance=updated_balance)
                )

        if update_values:
            await db.execute(
                update(CashFlowModel)
                .where(CashFlowModel.id == cashflow_id)
                .values(**update_values)
            )

        await db.commit()
        await db.refresh(db_cashflow)
        return db_cashflow

    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Integrity error updating cashflow {cashflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred.",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"SQLAlchemy error updating cashflow {cashflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating cashflow in database.",
        )
    except Exception as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Unexpected error updating cashflow {cashflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.delete("/{cashflow_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_cashflow_by_id(
    cashflow_id: int, db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Delete a cashflow transaction and reverse its effect on account balance.
    """
    try:
        result = await db.execute(
            select(CashFlowModel).where(CashFlowModel.id == cashflow_id)
        )
        db_cashflow = result.scalar_one_or_none()

        if db_cashflow is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CashFlow with ID {cashflow_id} not found",
            )

        result = await db.execute(
            select(AccountModel).where(AccountModel.id == db_cashflow.account_id)
        )
        db_account = result.scalar_one_or_none()

        if db_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated account not found",
            )

        new_balance = 0
        match db_cashflow.txn_type:
            case TransactionType.credit:
                new_balance = db_account.balance - db_cashflow.amount
            case TransactionType.debit:
                new_balance = db_account.balance + db_cashflow.amount

        await db.execute(
            update(AccountModel)
            .where(AccountModel.id == db_account.id)
            .values(balance=new_balance)
        )

        stmt = delete(CashFlowModel).where(CashFlowModel.id == cashflow_id)
        await db.execute(stmt)

        await db.commit()

        return {
            "message": "CashFlow deleted successfully",
            "cashflow_id": cashflow_id,
            "account_id": db_account.id,
        }

    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Integrity error deleting cashflow {cashflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred.",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"SQLAlchemy error deleting cashflow {cashflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting cashflow from database.",
        )
    except Exception as e:
        await db.rollback()
        if DEBUG:
            logger.error(f"Unexpected error deleting cashflow {cashflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
