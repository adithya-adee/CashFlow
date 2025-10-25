from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, delete, update
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..models import CashFlow as CashFlowModel, Account as AccountModel
from ..schema import CashFlow, CashFlowCreate, CashFlowEdit, TransactionType
from ..database import get_db


router = APIRouter(prefix="/cashflow", tags=["cashflow"])


@router.post("/add", response_model=CashFlow, status_code=status.HTTP_201_CREATED)
def create_cashflow(body: CashFlowCreate, db: Session = Depends(get_db)) -> CashFlow:
    """
    Create a new cashflow transaction.

    This endpoint records a new cashflow transaction (credit or debit) and
    automatically updates the balance of the associated bank account.

    Args:
        body (CashFlowCreate): The request body containing cashflow details.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        CashFlow: The newly created cashflow transaction with auto-generated ID and timestamps.

    Raises:
        HTTPException:
            - 404 Not Found: If the `account_id` provided does not correspond to an existing account.
            - 400 Bad Request: If a database integrity error occurs.
            - 422 Unprocessable Entity: If request body validation fails (e.g., amount <= 0).
            - 500 Internal Server Error: For any unexpected errors during processing.
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

        db_account = (
            db.query(AccountModel)
            .filter(AccountModel.id == db_cashflow.account_id)
            .first()
        )
        new_balance = 0

        if db_account is None:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account Not Found"
            )

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

        db.execute(stmt)

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
    Retrieve all cashflow transactions with pagination and filters.

    This endpoint fetches a list of cashflow transactions, allowing filtering by
    category, transaction type, and account ID, as well as pagination.

    Args:
        category (str, optional): An optional string to filter transactions by category. Defaults to None.
        txn_type (str, optional): An optional string to filter transactions by type ('credit' or 'debit'). Defaults to None.
        account_id (int, optional): An optional integer to filter transactions by the associated account ID. Defaults to None.
        skip (int, optional): The number of records to skip. Must be non-negative.
                            Defaults to 0.
        limit (int, optional): The maximum number of records to return. Must be
                            between 1 and 1000. Defaults to 100.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        list[CashFlow]: A list of cashflow transaction objects.

    Raises:
        HTTPException:
            - 422 Unprocessable Entity: If query parameters fail validation.
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
    Retrieve a single cashflow transaction by its ID.

    This endpoint fetches the details of a specific cashflow transaction using its unique ID.

    Args:
        cashflow_id (int): The unique identifier of the cashflow transaction to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        CashFlow: The cashflow transaction object matching the provided ID.

    Raises:
        HTTPException:
            - 404 Not Found: If no cashflow transaction with the given `cashflow_id` is found.
            - 422 Unprocessable Entity: If `cashflow_id` is not a valid integer.
    """
    cashflow = db.query(CashFlowModel).filter(CashFlowModel.id == cashflow_id).first()
    if cashflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CashFlow with ID {cashflow_id} not found",
        )
    return cashflow


@router.patch("/{cashflow_id}", response_model=CashFlow, status_code=status.HTTP_200_OK)
def edit_cashflow_by_id(
    cashflow_id: int, body: CashFlowEdit, db: Session = Depends(get_db)
) -> CashFlow:
    """
    Edit an existing cashflow transaction by ID.

    This endpoint allows partial updates to an existing cashflow transaction. Only the fields
    provided in the request body will be updated. It also correctly adjusts the associated
    account's balance based on changes to amount, transaction type, or account ID.

    Args:
        cashflow_id (int): The unique identifier of the cashflow transaction to update.
        body (CashFlowEdit): The request body containing the fields to update.
                            All fields are optional.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        CashFlow: The updated cashflow transaction object.

    Raises:
        HTTPException:
            - 404 Not Found: If the cashflow transaction or an associated account is not found.
            - 400 Bad Request: If a database integrity error occurs during the update.
            - 422 Unprocessable Entity: If request body or path parameters fail validation.
            - 500 Internal Server Error: For any unexpected errors during processing.
    """
    try:
        db_cashflow = (
            db.query(CashFlowModel).filter(CashFlowModel.id == cashflow_id).first()
        )
        if db_cashflow is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cashflow not found"
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
            old_account = (
                db.query(AccountModel)
                .filter(AccountModel.id == db_cashflow.account_id)
                .first()
            )

            if old_account is None:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Old Account not found",
                )

            old_balance_adjustment = 0
            match db_cashflow.txn_type:
                case TransactionType.credit:
                    old_balance_adjustment = -db_cashflow.amount  # Remove credit
                case TransactionType.debit:
                    old_balance_adjustment = db_cashflow.amount  # Remove debit

            if "account_id" in update_values:
                new_account = (
                    db.query(AccountModel)
                    .filter(AccountModel.id == final_account_id)
                    .first()
                )

                if new_account is None:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="New Account not found",
                    )

                new_old_balance = old_account.balance + old_balance_adjustment
                db.execute(
                    update(AccountModel)
                    .where(AccountModel.id == old_account.id)
                    .values(balance=new_old_balance)
                )

                new_balance_adjustment = 0
                match final_txn_type:
                    case TransactionType.credit:
                        new_balance_adjustment = final_amount
                    case TransactionType.debit:
                        new_balance_adjustment = -final_amount

                new_balance = new_account.balance + new_balance_adjustment
                db.execute(
                    update(AccountModel)
                    .where(AccountModel.id == new_account.id)
                    .values(balance=new_balance)
                )
            else:
                # Same account, just update with net change
                # Reverse old transaction and apply new transaction
                new_balance_adjustment = 0
                match final_txn_type:
                    case TransactionType.credit:
                        new_balance_adjustment = final_amount
                    case TransactionType.debit:
                        new_balance_adjustment = -final_amount

                new_balance = (
                    old_account.balance
                    + old_balance_adjustment
                    + new_balance_adjustment
                )
                db.execute(
                    update(AccountModel)
                    .where(AccountModel.id == old_account.id)
                    .values(balance=new_balance)
                )

        if update_values:
            db.execute(
                update(CashFlowModel)
                .where(CashFlowModel.id == cashflow_id)
                .values(**update_values)
            )

        db.commit()
        db.refresh(db_cashflow)
        return db_cashflow

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred",
        )
    except HTTPException:
        # Re-raise HTTP exceptions (they already have rollback)
        raise
    except Exception as e:
        # Catch any other exceptions and rollback
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.delete("/{cashflow_id}", response_model=bool, status_code=status.HTTP_200_OK)
def delete_cashflow_by_id(cashflow_id: int, db: Session = Depends(get_db)) -> bool:
    """
    Delete a cashflow transaction by ID.

    This endpoint deletes a cashflow transaction and reverses its financial effect
    on the associated bank account's balance.

    Args:
        cashflow_id (int): The unique identifier of the cashflow transaction to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        None: No content is returned upon successful deletion (204 No Content).

    Raises:
        HTTPException:
            - 404 Not Found: If the cashflow transaction or its associated account is not found.
            - 400 Bad Request: If a database integrity error occurs during deletion.
            - 422 Unprocessable Entity: If `cashflow_id` is not a valid integer.
            - 500 Internal Server Error: For any unexpected errors during processing.
    """
    try:
        db_cashflow = (
            db.query(CashFlowModel).filter(CashFlowModel.id == cashflow_id).first()
        )

        if db_cashflow is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CashFlow with ID {cashflow_id} not found",
            )

        db_account = (
            db.query(AccountModel)
            .filter(AccountModel.id == db_cashflow.account_id)
            .first()
        )

        if db_account is None:
            db.rollback()
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

        # Update account balance
        db.execute(
            update(AccountModel)
            .where(AccountModel.id == db_account.id)
            .values(balance=new_balance)
        )

        # Delete the cashflow
        stmt = delete(CashFlowModel).where(CashFlowModel.id == cashflow_id)
        db.execute(stmt)

        db.commit()
        return True

    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
