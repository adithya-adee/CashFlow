from enum import Enum


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
