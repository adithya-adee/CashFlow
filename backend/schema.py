from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from enum import Enum


# ENUMS class TransactionType(str, Enum):
class TransactionType(str, Enum):
    credit = "credit"
    debit = "debit"


class AccountType(str, Enum):
    savings = "savings"
    current_account = "current_account"
    fd_account = "fd_account"
    rd_account = "rd_account"
    demat_account = "demat_account"


class Currency(str, Enum):
    USD = "USD"
    INR = "INR"


# MODALS
class AccountBase(BaseModel):
    bank_account_no: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, to_upper=True, min_length=10, max_length=50
        ),
    ]
    bank_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)
    ]
    account_type: AccountType = AccountType.savings
    holder_name: str
    balance: float
    currency: Currency = Currency.INR


class AccountCreate(AccountBase):
    balance: float = 0

    @field_validator("balance")
    @classmethod
    def amount_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Amount must be positive value")
        return value


class Account(AccountBase):
    id: int
    created_at: datetime


class CashFlowBase(BaseModel):
    account_id: int
    txn_type: TransactionType
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Amount must be positive value")
        return value


class CashFlow(CashFlowBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # For Pydantic V2 ORM mode
    model_config = ConfigDict(from_attributes=True)
