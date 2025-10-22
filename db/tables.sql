CREATE TABLE IF NOT EXISTS ACCOUNT (
    id TEXT PRIMARY KEY,
    bank_account_no TEXT UNIQUE,
    bank_name TEXT,
    account_type TEXT DEFAULT 'savings',
    holder_name TEXT,
    balance REAL DEFAULT 0.0,
    currency TEXT DEFAULT 'INR',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CASHFLOW (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    txn_type TEXT CHECK (txn_type IN ('credit', 'debit')),
    category TEXT,
    amount REAL NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES ACCOUNT(id) ON DELETE CASCADE
);
