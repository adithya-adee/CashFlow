from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class CashFlow(Base):
    __tablename__ = "cashflow"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(
        Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    txn_type = Column(String, nullable=False, index=True)
    category = Column(String, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())  # Uses SQL CURRENT_TIMESTAMP
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now()
    )  # Uses SQL CURRENT_TIMESTAMP

    # Add check constraint for txn_type
    __table_args__ = (
        CheckConstraint("txn_type IN ('credit', 'debit')", name="check_txn_type"),
    )

    # Relationship
    account = relationship("Account", back_populates="cashflows")
