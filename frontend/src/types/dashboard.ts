// TypeScript interfaces for Dashboard schema
import type { Account } from './account';
import type { CashFlow } from './cash_flow';

export interface DashboardStats {
  total_balance: number;
  total_income: number;
  total_expense: number;
  recent_transactions: CashFlow[];
  account_overview: Account[];
}

export interface SuperDashboardQuery {
  category?: string;
  gt_amount?: number;
  lt_amount?: number;
  txn_type?: string;
  account_id?: number;
}
