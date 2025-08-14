// Transaction types and enums matching backend schema
export type TransactionType = 'credit' | 'debit';
export type TransactionCategoryType = 'income' | 'expense' | 'transfer';
export type RecurringFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';

// Core Transaction interface
export interface Transaction {
  id: number;
  tenant_id: number;
  user_id: number;
  type: TransactionType;
  amount: number; // Decimal from backend as number in frontend
  currency: string;
  description?: string;
  transaction_date: string; // ISO date string
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
  reference_number?: string;
  is_recurring: boolean;
  recurring_template_id?: number;
  attachments?: Record<string, unknown>;
  extra_data?: Record<string, unknown>;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

// Transaction creation interface
export interface TransactionCreate {
  type: TransactionType;
  amount: number;
  currency?: string;
  description?: string;
  transaction_date: string; // ISO date string
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
  reference_number?: string;
  is_recurring?: boolean;
  recurring_template_id?: number;
  attachments?: Record<string, unknown>;
  extra_data?: Record<string, unknown>;
}

// Transaction update interface
export interface TransactionUpdate {
  type?: TransactionType;
  amount?: number;
  currency?: string;
  description?: string;
  transaction_date?: string; // ISO date string
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
  reference_number?: string;
  is_recurring?: boolean;
  recurring_template_id?: number;
  attachments?: Record<string, unknown>;
  extra_data?: Record<string, unknown>;
}

// Transaction with details (includes related entities)
export interface TransactionWithDetails extends Transaction {
  category?: TransactionCategory;
  subcategory?: TransactionSubcategory;
  account?: FinancialAccount;
  recurring_template?: RecurringTransaction;
}

// Transaction Category interface
export interface TransactionCategory {
  id: number;
  tenant_id: number;
  user_id?: number;
  name: string;
  type?: TransactionCategoryType;
  color?: string; // Hex color code
  icon?: string;
  is_system: boolean;
  created_at: string; // ISO string
}

// Transaction Category creation interface
export interface TransactionCategoryCreate {
  name: string;
  type?: TransactionCategoryType;
  color?: string;
  icon?: string;
}

// Transaction Category update interface
export interface TransactionCategoryUpdate {
  name?: string;
  type?: TransactionCategoryType;
  color?: string;
  icon?: string;
}

// Transaction Category with subcategories
export interface TransactionCategoryWithSubcategories extends TransactionCategory {
  subcategories: TransactionSubcategory[];
}

// Transaction Subcategory interface
export interface TransactionSubcategory {
  id: number;
  tenant_id: number;
  user_id?: number;
  category_id: number;
  name: string;
  color?: string;
  icon?: string;
  is_system: boolean;
  created_at: string; // ISO string
}

// Transaction Subcategory creation interface
export interface TransactionSubcategoryCreate {
  category_id: number;
  name: string;
  color?: string;
  icon?: string;
}

// Transaction Subcategory update interface
export interface TransactionSubcategoryUpdate {
  name?: string;
  color?: string;
  icon?: string;
}

// Financial Account interface
export interface FinancialAccount {
  id: number;
  tenant_id: number;
  user_id: number;
  account_name: string;
  account_type?: string;
  account_number?: string;
  bank_name?: string;
  current_balance: number; // Decimal from backend as number in frontend
  currency: string;
  is_active: boolean;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

// Financial Account creation interface
export interface FinancialAccountCreate {
  account_name: string;
  account_type?: string;
  account_number?: string;
  bank_name?: string;
  current_balance?: number;
  currency?: string;
  is_active?: boolean;
}

// Financial Account update interface
export interface FinancialAccountUpdate {
  account_name?: string;
  account_type?: string;
  account_number?: string;
  bank_name?: string;
  current_balance?: number;
  currency?: string;
  is_active?: boolean;
}

// Financial Account with summary
export interface FinancialAccountWithSummary extends FinancialAccount {
  transaction_count: number;
  total_credits: number;
  total_debits: number;
  last_transaction_date?: string; // ISO string
}

// Recurring Transaction interface
export interface RecurringTransaction {
  id: number;
  tenant_id: number;
  user_id: number;
  template_name: string;
  type: TransactionType;
  amount: number; // Decimal from backend as number in frontend
  currency: string;
  description?: string;
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
  frequency: RecurringFrequency;
  interval_count: number;
  start_date: string; // ISO date string
  end_date?: string; // ISO date string
  reminder_days: number;
  is_active: boolean;
  next_due_date?: string; // ISO date string
  extra_data?: Record<string, unknown>;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

// Recurring Transaction creation interface
export interface RecurringTransactionCreate {
  template_name: string;
  type: TransactionType;
  amount: number;
  currency?: string;
  description?: string;
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
  frequency: RecurringFrequency;
  interval_count?: number;
  start_date: string; // ISO date string
  end_date?: string; // ISO date string
  reminder_days?: number;
  is_active?: boolean;
  extra_data?: Record<string, unknown>;
}

// Recurring Transaction update interface
export interface RecurringTransactionUpdate {
  template_name?: string;
  type?: TransactionType;
  amount?: number;
  currency?: string;
  description?: string;
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
  frequency?: RecurringFrequency;
  interval_count?: number;
  start_date?: string; // ISO date string
  end_date?: string; // ISO date string
  reminder_days?: number;
  is_active?: boolean;
  extra_data?: Record<string, unknown>;
}

// Recurring Transaction with next occurrence info
export interface RecurringTransactionWithNext extends RecurringTransaction {
  next_occurrence_date?: string; // ISO date string
  days_until_next?: number;
}

// Filtering interfaces
export interface TransactionFilters {
  type?: TransactionType;
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
  date_from?: string; // ISO date string
  date_to?: string; // ISO date string
  amount_min?: number;
  amount_max?: number;
  currency?: string;
  description?: string;
  is_recurring?: boolean;
}

// Search interface
export interface TransactionSearchQuery {
  query: string;
  filters?: TransactionFilters;
  sort_by?: 'date' | 'amount' | 'description' | 'created_at';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

// Bulk operations
export interface TransactionBulkUpdate {
  transaction_ids: number[];
  category_id?: number;
  subcategory_id?: number;
  account_id?: number;
}

// Constants for UI
export const TRANSACTION_TYPE_OPTIONS: { value: TransactionType; label: string; color: string }[] = [
  { value: 'credit', label: 'Credit (Income)', color: 'green' },
  { value: 'debit', label: 'Debit (Expense)', color: 'red' },
];

export const TRANSACTION_CATEGORY_TYPE_OPTIONS: { value: TransactionCategoryType; label: string; color: string }[] = [
  { value: 'income', label: 'Income', color: 'green' },
  { value: 'expense', label: 'Expense', color: 'red' },
  { value: 'transfer', label: 'Transfer', color: 'blue' },
];

export const RECURRING_FREQUENCY_OPTIONS: { value: RecurringFrequency; label: string }[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'yearly', label: 'Yearly' },
];

// Additional interfaces for state management
export interface TransactionSortBy {
  field: 'date' | 'amount' | 'description' | 'created_at';
  direction: 'asc' | 'desc';
}

export interface TransactionFormData {
  type: TransactionType;
  amount: string; // String for form input
  currency: string;
  description: string;
  transaction_date: string;
  category_id: string; // String for form select
  subcategory_id: string; // String for form select
  account_id: string; // String for form select
  reference_number: string;
  is_recurring: boolean;
  recurring_template_id: string; // String for form select
}

export interface ValidationErrors {
  type?: string;
  amount?: string;
  currency?: string;
  description?: string;
  transaction_date?: string;
  category_id?: string;
  subcategory_id?: string;
  account_id?: string;
  reference_number?: string;
  general?: string;
}

export type CreateTransactionInput = TransactionCreate;
export type CreateCategoryInput = TransactionCategoryCreate;
export type CreateAccountInput = FinancialAccountCreate;
export type CreateRecurringTransactionInput = RecurringTransactionCreate;

// View mode for transaction display
export type TransactionViewMode = 'list' | 'table' | 'calendar' | 'chart';

// Transaction summary interfaces
export interface TransactionSummary {
  total_income: number;
  total_expenses: number;
  net_amount: number;
  transaction_count: number;
  currency: string;
  period_start: string; // ISO date string
  period_end: string; // ISO date string
}

export interface CategorySummary {
  category_id: number;
  category_name: string;
  total_amount: number;
  transaction_count: number;
  percentage: number;
}

export interface AccountSummary {
  account_id: number;
  account_name: string;
  current_balance: number;
  total_credits: number;
  total_debits: number;
  transaction_count: number;
  currency: string;
}