from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from schema.enums import Currency, AccountType


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
    currency: Currency = Currency.INR

    @field_validator("account_type", mode="before")
    @classmethod
    def validate_account_type(cls, value):
        if isinstance(value, str):
            try:
                return AccountType(value)
            except ValueError:
                raise ValueError(
                    f"Invalid account type: {value}. Must be one of {[e.value for e in AccountType]}"
                )
        return value

    @field_validator("currency", mode="before")
    @classmethod
    def validate_currency(cls, value):
        if isinstance(value, str):
            try:
                return Currency(value)
            except ValueError:
                raise ValueError(
                    f"Invalid currency: {value}. Must be one of {[e.value for e in Currency]}"
                )
        return value


class AccountCreate(AccountBase):
    balance: float = 0.0

    @field_validator("balance")
    @classmethod
    def non_negative_balance(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Balance shouldn't be less than 0")
        return value


class AccountEdit(BaseModel):
    bank_account_no: Optional[str] = None
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    holder_name: Optional[str] = None
    currency: Optional[str] = None
    balance: Optional[float] = None

    @field_validator("balance")
    @classmethod
    def non_negative_balance(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Balance shouldn't be less than 0")
        return value


class Account(AccountBase):
    id: int
    balance: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
