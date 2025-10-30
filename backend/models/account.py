from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bank_account_no = Column(String, unique=True, nullable=False)
    bank_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False, default="savings")
    holder_name = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="INR")
    created_at = Column(DateTime, default=func.now())  # Uses SQL CURRENT_TIMESTAMP
    updated_at = Column(DateTime, default=func.now())  # Uses SQL CURRENT_TIMESTAMP

    # Relationship
    cashflows = relationship(
        "CashFlow", back_populates="account", cascade="all, delete-orphan"
    )
