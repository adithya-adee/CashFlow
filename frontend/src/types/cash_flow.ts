// TypeScript interfaces for CashFlow schema

// Transaction type matching backend enum
export type TransactionType = 'credit' | 'debit';

// Category type as union of string literals
export type Category =
  // Income Categories
  | 'income'
  | 'salary'
  | 'freelance'
  | 'investment'
  | 'refund'
  | 'gift_received'
  | 'rental_income'
  | 'bonus'
  | 'interest'
  | 'reimbursement'
  | 'parental_contribution'
  | 'pension'
  | 'dividends'
  | 'tax_refund'
  // Expense Categories
  | 'rent'
  | 'mortgage'
  | 'utilities'
  | 'internet'
  | 'mobile_phone'
  | 'insurance'
  | 'property_tax'
  | 'home_maintenance'
  | 'grocery'
  | 'dining_out'
  | 'coffee'
  | 'snacks'
  | 'car_payment'
  | 'fuel'
  | 'public_transit'
  | 'ride_share'
  | 'parking'
  | 'car_maintenance'
  | 'health_care'
  | 'medication'
  | 'personal_care'
  | 'gym'
  | 'clothing'
  | 'subscriptions'
  | 'entertainment'
  | 'hobby'
  | 'travel'
  | 'vacation'
  | 'debt_payment'
  | 'student_loan'
  | 'bank_fee'
  | 'savings'
  | 'sip'
  | 'education'
  | 'gifts_given'
  | 'donations'
  | 'pet_care'
  | 'child_care'
  | 'cash_withdrawal'
  | 'miscellaneous';
export interface CashFlow {
  id: number;
  account_id: number;
  txn_type: TransactionType;
  amount: number;
  category?: Category;
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

export interface CashFlowList {
  data: CashFlow[];
  page_size: number;
  page_number: number;
  total_count: number;
}
