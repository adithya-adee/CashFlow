from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

from schema.enums import TransactionType


class SuperDashboardQuery(BaseModel):
    category: Optional[str] = None
    gt_amount: Optional[float] = None
    lt_amount: Optional[float] = None
    txn_type: Optional[str] = None
    account_id: Optional[int] = None

    @field_validator("gt_amount", "lt_amount")
    @classmethod
    def amount_must_be_positive(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        elif value <= 0:
            raise ValueError("Amount must be a positive value if provided")
        return value

    @field_validator("txn_type")
    @classmethod
    def txn_type_verify(cls, value: Optional[str]) -> Optional[TransactionType]:
        if value is None:
            return None

        lower_value = value.lower()

        match lower_value:
            case "debit":
                return TransactionType.debit
            case "credit":
                return TransactionType.credit
            case _:
                raise ValueError(
                    "Invalid transaction type. Must be 'debit' or 'credit'."
                )

    @model_validator(mode="after")
    def check_amount_ranges(self) -> "SuperDashboardQuery":
        if self.gt_amount is not None and self.lt_amount is not None:
            if self.gt_amount > self.lt_amount:
                raise ValueError(
                    "Greater than amount (gt_amount) cannot be greater than less than amount (lt_amount)."
                )
        return self
