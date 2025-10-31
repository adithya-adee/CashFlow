// TypeScript interfaces for Account schema

// Types matching backend enums
export type AccountType = 'savings' | 'current_account' | 'fd_account' | 'rd_account' | 'demat_account';
export type Currency = 'USD' | 'INR';

export interface Account {
  id: number;
  bank_account_no: string;
  bank_name: string;
  account_type: AccountType;
  holder_name: string;
  currency: Currency;
  balance: number;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  bank_account_no: string;
  bank_name: string;
  account_type: AccountType;
  holder_name: string;
  currency: Currency;
  balance?: number;
}

export interface AccountEdit {
  bank_account_no?: string;
  bank_name?: string;
  account_type?: string;
  holder_name?: string;
  currency?: string;
  balance?: number;
}
