from sqlalchemy import Column, Integer, String, Float, DateTime
from ..database import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    bank_account_no = Column(String, unique=True)
    bank_name = Column(String)
    account_type = Column(String, default="savings")
    holder_name = Column(String)
    balance = Column(Float, default=0.0)
    currency = Column(String, default="INR")
    created_at = Column(DateTime)
