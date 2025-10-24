from datetime import datetime, timezone  # Import both datetime class and timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from ..database import Base


class CashFlow(Base):
    __tablename__ = "cashflow"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id"), index=True)
    txn_type = Column(String, index=True)
    category = Column(String, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )