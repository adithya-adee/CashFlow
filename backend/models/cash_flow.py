from sqlalchemy import Column, Integer, String, Float, DateTime
from ..database import Base


class CashFlow(Base):
    __tablename__ = "cashflow"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)
    txn_type = Column(String, index=True)
    category = Column(String, index=True)
    amount = Column(Float)
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    created_at = Column(DateTime)
