CREATE TABLE "ACCOUNT" (
	"id"	INTEGER,
	"bank_account_no"	TEXT NOT NULL UNIQUE,
	"bank_name"	TEXT NOT NULL,
	"account_type"	TEXT NOT NULL DEFAULT 'savings',
	"holder_name"	TEXT NOT NULL,
	"balance"	REAL NOT NULL DEFAULT 0.0,
	"currency"	TEXT NOT NULL DEFAULT 'INR',
	"created_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	datetime DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id")
);

CREATE TABLE "CASHFLOW" (
	"id"	INTEGER,
	"account_id"	INTEGER NOT NULL,
	"txn_type"	TEXT NOT NULL CHECK("txn_type" IN ('credit', 'debit')),
	"category"	TEXT,
	"amount"	REAL NOT NULL,
	"description"	TEXT,
	"created_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("account_id") REFERENCES "ACCOUNT"("id") ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
