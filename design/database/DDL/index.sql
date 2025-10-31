CREATE INDEX idx_cashflow_account_id ON CASHFLOW (account_id);
CREATE INDEX idx_cashflow_category ON CASHFLOW (category);
CREATE INDEX idx_cashflow_txn_type ON CASHFLOW (txn_type);
CREATE INDEX idx_cashflow_composite_search ON CASHFLOW (account_id, category, txn_type);