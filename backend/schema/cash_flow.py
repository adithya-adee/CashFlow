from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from .enums import TransactionType


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
            raise ValueError("Amount must be a positive value")
        return value


class CashFlowCreate(CashFlowBase):
    pass


class CashFlow(CashFlowBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
