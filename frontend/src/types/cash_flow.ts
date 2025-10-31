// TypeScript interfaces for CashFlow schema

// Transaction type matching backend enum
export type TransactionType = 'credit' | 'debit';

export interface CashFlow {
  id: number;
  account_id: number;
  txn_type: TransactionType;
  amount: number;
  category?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CashFlowCreate {
  account_id: number;
  txn_type: TransactionType;
  amount: number;
  category?: string;
  description?: string;
}

export interface CashFlowEdit {
  account_id?: number;
  txn_type?: TransactionType;
  amount?: number;
  category?: string;
  description?: string;
}
