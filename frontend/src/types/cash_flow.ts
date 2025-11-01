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


export interface CashFlowWithAccountDetails extends CashFlow{
  bank_account_no : string,
  currency : string
}

export interface CashFlowList {
  data: CashFlowWithAccountDetails[];
  page_size: number;
  page_number: number;
  total_count: number;
}

// Category options for dropdown
export const categoryOptions = [
  { value: 'bank_fee', label: 'Bank Fee' },
  { value: 'bonus', label: 'Bonus' },
  { value: 'cash_withdrawal', label: 'Cash Withdrawal' },
  { value: 'car_maintenance', label: 'Car Maintenance' },
  { value: 'car_payment', label: 'Car Payment' },
  { value: 'child_care', label: 'Child Care' },
  { value: 'clothing', label: 'Clothing' },
  { value: 'coffee', label: 'Coffee' },
  { value: 'debt_payment', label: 'Debt Payment' },
  { value: 'dining_out', label: 'Dining Out' },
  { value: 'dividends', label: 'Dividends' },
  { value: 'donations', label: 'Donations' },
  { value: 'education', label: 'Education' },
  { value: 'entertainment', label: 'Entertainment' },
  { value: 'freelance', label: 'Freelance' },
  { value: 'fuel', label: 'Fuel' },
  { value: 'gift_received', label: 'Gift Received' },
  { value: 'gifts_given', label: 'Gifts Given' },
  { value: 'grocery', label: 'Grocery' },
  { value: 'gym', label: 'Gym' },
  { value: 'health_care', label: 'Health Care' },
  { value: 'home_maintenance', label: 'Home Maintenance' },
  { value: 'income', label: 'Income' },
  { value: 'insurance', label: 'Insurance' },
  { value: 'interest', label: 'Interest' },
  { value: 'internet', label: 'Internet' },
  { value: 'investment', label: 'Investment' },
  { value: 'medication', label: 'Medication' },
  { value: 'miscellaneous', label: 'Miscellaneous' },
  { value: 'mobile_phone', label: 'Mobile Phone' },
  { value: 'mortgage', label: 'Mortgage' },
  { value: 'parental_contribution', label: 'Parental Contribution' },
  { value: 'parking', label: 'Parking' },
  { value: 'pension', label: 'Pension' },
  { value: 'property_tax', label: 'Property Tax' },
  { value: 'public_transit', label: 'Public Transit' },
  { value: 'rental_income', label: 'Rental Income' },
  { value: 'refund', label: 'Refund' },
  { value: 'reimbursement', label: 'Reimbursement' },
  { value: 'rent', label: 'Rent' },
  { value: 'ride_share', label: 'Ride Share' },
  { value: 'savings', label: 'Savings' },
  { value: 'salary', label: 'Salary' },
  { value: 'sip', label: 'SIP' },
  { value: 'snacks', label: 'Snacks' },
  { value: 'student_loan', label: 'Student Loan' },
  { value: 'subscriptions', label: 'Subscriptions' },
  { value: 'tax_refund', label: 'Tax Refund' },
  { value: 'travel', label: 'Travel' },
  { value: 'vacation', label: 'Vacation' },
  { value: 'utilities', label: 'Utilities' },
];
