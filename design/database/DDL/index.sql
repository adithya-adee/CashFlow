
CREATE INDEX account_filter ON CASHFLOW (account_id);
CREATE INDEX category_filter ON CASHFLOW (category);
CREATE INDEX cashflow_search ON CASHFLOW (account_id, category, txn_type);
