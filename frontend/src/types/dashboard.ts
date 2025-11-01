// TypeScript interfaces for Dashboard schema
// import type { Account } from '@/types/account';
import type { CashFlow } from '@/types/cash_flow';

export interface DashboardStats {
  total_counts: {
    total_accounts: number;
    total_cashflows: number;
    total_credits_count: number;
    total_debits_count: number;
  };

  balance_summary: {
    total_balance: number;
    total_credits: number;
    total_debits: number;
  };
  recent_transactions: CashFlow[];
  // account_overview: Account[];
}

export interface SuperDashboardQuery {
  category?: string;
  gt_amount?: number;
  lt_amount?: number;
  txn_type?: string;
  account_id?: number;
}
