import api from './api';
import { AxiosError } from 'axios';
import {
  Transaction,
  TransactionCreate,
  TransactionUpdate,
  TransactionWithDetails,
  TransactionCategory,
  TransactionCategoryCreate,
  TransactionCategoryUpdate,
  TransactionCategoryWithSubcategories,
  TransactionSubcategory,
  TransactionSubcategoryCreate,
  TransactionSubcategoryUpdate,
  FinancialAccount,
  FinancialAccountCreate,
  FinancialAccountUpdate,
  FinancialAccountWithSummary,
  RecurringTransaction,
  RecurringTransactionCreate,
  RecurringTransactionUpdate,
  RecurringTransactionWithNext,
  TransactionFilters,
  TransactionSearchQuery,
  TransactionBulkUpdate,
  TransactionSummary,
  CategorySummary,
  AccountSummary,
} from '../types/Transaction';

class TransactionsService {
  // Transaction CRUD operations
  async getTransactions(skip: number = 0, limit: number = 100, filters?: TransactionFilters): Promise<Transaction[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    // Add filters to query params
    if (filters) {
      if (filters.type) params.append('type', filters.type);
      if (filters.category_id) params.append('category_id', filters.category_id.toString());
      if (filters.subcategory_id) params.append('subcategory_id', filters.subcategory_id.toString());
      if (filters.account_id) params.append('account_id', filters.account_id.toString());
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      if (filters.amount_min !== undefined) params.append('amount_min', filters.amount_min.toString());
      if (filters.amount_max !== undefined) params.append('amount_max', filters.amount_max.toString());
      if (filters.currency) params.append('currency', filters.currency);
      if (filters.description) params.append('description', filters.description);
      if (filters.is_recurring !== undefined) params.append('is_recurring', filters.is_recurring.toString());
    }

    const response = await api.get<Transaction[]>(`/transactions/?${params.toString()}`);
    return response.data;
  }

  async getTransaction(transactionId: number): Promise<TransactionWithDetails> {
    const response = await api.get<TransactionWithDetails>(`/transactions/${transactionId}`);
    return response.data;
  }

  async createTransaction(transactionData: TransactionCreate): Promise<Transaction> {
    const response = await api.post<Transaction>('/transactions/', transactionData);
    return response.data;
  }

  async updateTransaction(transactionId: number, transactionData: TransactionUpdate): Promise<Transaction> {
    const response = await api.put<Transaction>(`/transactions/${transactionId}`, transactionData);
    return response.data;
  }

  async deleteTransaction(transactionId: number): Promise<void> {
    await api.delete(`/transactions/${transactionId}`);
  }

  async bulkUpdateTransactions(bulkUpdate: TransactionBulkUpdate): Promise<Transaction[]> {
    const response = await api.put<Transaction[]>('/transactions/bulk', bulkUpdate);
    return response.data;
  }

  async bulkDeleteTransactions(transactionIds: number[]): Promise<void> {
    await api.delete('/transactions/bulk', { data: { transaction_ids: transactionIds } });
  }

  // Transaction search
  async searchTransactions(searchQuery: TransactionSearchQuery): Promise<Transaction[]> {
    const params = new URLSearchParams({
      query: searchQuery.query,
    });

    if (searchQuery.filters) {
      Object.entries(searchQuery.filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }

    if (searchQuery.sort_by) params.append('sort_by', searchQuery.sort_by);
    if (searchQuery.sort_order) params.append('sort_order', searchQuery.sort_order);
    if (searchQuery.limit) params.append('limit', searchQuery.limit.toString());
    if (searchQuery.offset) params.append('offset', searchQuery.offset.toString());

    const response = await api.get<Transaction[]>(`/transactions/search?${params.toString()}`);
    return response.data;
  }

  // Transaction Categories
  async getTransactionCategories(skip: number = 0, limit: number = 100): Promise<TransactionCategory[]> {
    const response = await api.get<TransactionCategory[]>(`/transaction-categories/?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getTransactionCategoriesWithSubcategories(): Promise<TransactionCategoryWithSubcategories[]> {
    const response = await api.get<TransactionCategoryWithSubcategories[]>('/transaction-categories/with-subcategories');
    return response.data;
  }

  async getTransactionCategory(categoryId: number): Promise<TransactionCategory> {
    const response = await api.get<TransactionCategory>(`/transaction-categories/${categoryId}`);
    return response.data;
  }

  async createTransactionCategory(categoryData: TransactionCategoryCreate): Promise<TransactionCategory> {
    const response = await api.post<TransactionCategory>('/transaction-categories/', categoryData);
    return response.data;
  }

  async updateTransactionCategory(categoryId: number, categoryData: TransactionCategoryUpdate): Promise<TransactionCategory> {
    const response = await api.put<TransactionCategory>(`/transaction-categories/${categoryId}`, categoryData);
    return response.data;
  }

  async deleteTransactionCategory(categoryId: number): Promise<void> {
    await api.delete(`/transaction-categories/${categoryId}`);
  }

  // Transaction Subcategories
  async getTransactionSubcategories(categoryId?: number): Promise<TransactionSubcategory[]> {
    const params = categoryId ? `?category_id=${categoryId}` : '';
    const response = await api.get<TransactionSubcategory[]>(`/transaction-subcategories/${params}`);
    return response.data;
  }

  async createTransactionSubcategory(subcategoryData: TransactionSubcategoryCreate): Promise<TransactionSubcategory> {
    const response = await api.post<TransactionSubcategory>('/transaction-subcategories/', subcategoryData);
    return response.data;
  }

  async updateTransactionSubcategory(subcategoryId: number, subcategoryData: TransactionSubcategoryUpdate): Promise<TransactionSubcategory> {
    const response = await api.put<TransactionSubcategory>(`/transaction-subcategories/${subcategoryId}`, subcategoryData);
    return response.data;
  }

  async deleteTransactionSubcategory(subcategoryId: number): Promise<void> {
    await api.delete(`/transaction-subcategories/${subcategoryId}`);
  }

  // Financial Accounts
  async getFinancialAccounts(skip: number = 0, limit: number = 100): Promise<FinancialAccount[]> {
    const response = await api.get<FinancialAccount[]>(`/financial-accounts/?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getFinancialAccountsWithSummary(): Promise<FinancialAccountWithSummary[]> {
    const response = await api.get<FinancialAccountWithSummary[]>('/financial-accounts/with-summary');
    return response.data;
  }

  async getFinancialAccount(accountId: number): Promise<FinancialAccount> {
    const response = await api.get<FinancialAccount>(`/financial-accounts/${accountId}`);
    return response.data;
  }

  async createFinancialAccount(accountData: FinancialAccountCreate): Promise<FinancialAccount> {
    const response = await api.post<FinancialAccount>('/financial-accounts/', accountData);
    return response.data;
  }

  async updateFinancialAccount(accountId: number, accountData: FinancialAccountUpdate): Promise<FinancialAccount> {
    const response = await api.put<FinancialAccount>(`/financial-accounts/${accountId}`, accountData);
    return response.data;
  }

  async deleteFinancialAccount(accountId: number): Promise<void> {
    await api.delete(`/financial-accounts/${accountId}`);
  }

  // Recurring Transactions
  async getRecurringTransactions(skip: number = 0, limit: number = 100): Promise<RecurringTransaction[]> {
    const response = await api.get<RecurringTransaction[]>(`/recurring-transactions/?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getRecurringTransactionsWithNext(): Promise<RecurringTransactionWithNext[]> {
    const response = await api.get<RecurringTransactionWithNext[]>('/recurring-transactions/with-next');
    return response.data;
  }

  async getRecurringTransaction(recurringId: number): Promise<RecurringTransaction> {
    const response = await api.get<RecurringTransaction>(`/recurring-transactions/${recurringId}`);
    return response.data;
  }

  async createRecurringTransaction(recurringData: RecurringTransactionCreate): Promise<RecurringTransaction> {
    const response = await api.post<RecurringTransaction>('/recurring-transactions/', recurringData);
    return response.data;
  }

  async updateRecurringTransaction(recurringId: number, recurringData: RecurringTransactionUpdate): Promise<RecurringTransaction> {
    const response = await api.put<RecurringTransaction>(`/recurring-transactions/${recurringId}`, recurringData);
    return response.data;
  }

  async deleteRecurringTransaction(recurringId: number): Promise<void> {
    await api.delete(`/recurring-transactions/${recurringId}`);
  }

  async getDueRecurringTransactions(daysAhead: number = 7): Promise<RecurringTransactionWithNext[]> {
    const response = await api.get<RecurringTransactionWithNext[]>(`/recurring-transactions/due-reminders?days_ahead=${daysAhead}`);
    return response.data;
  }

  async processRecurringTransactions(dryRun: boolean = false): Promise<Transaction[]> {
    const response = await api.post<Transaction[]>(`/background-tasks/recurring-transactions/process?dry_run=${dryRun}`);
    return response.data;
  }

  // Analytics and Reporting
  async getTransactionSummary(
    dateFrom?: string,
    dateTo?: string,
    categoryId?: number,
    accountId?: number
  ): Promise<TransactionSummary> {
    const params = new URLSearchParams();
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (categoryId) params.append('category_id', categoryId.toString());
    if (accountId) params.append('account_id', accountId.toString());

    const response = await api.get<TransactionSummary>(`/transactions/summary?${params.toString()}`);
    return response.data;
  }

  async getCategorySummary(
    dateFrom?: string,
    dateTo?: string,
    transactionType?: 'credit' | 'debit'
  ): Promise<CategorySummary[]> {
    const params = new URLSearchParams();
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (transactionType) params.append('type', transactionType);

    const response = await api.get<CategorySummary[]>(`/transactions/category-summary?${params.toString()}`);
    return response.data;
  }

  async getAccountSummary(): Promise<AccountSummary[]> {
    const response = await api.get<AccountSummary[]>('/transactions/account-summary');
    return response.data;
  }

  // Utility methods
  async validateTransactionData(transactionData: TransactionCreate): Promise<{ valid: boolean; errors?: string[] }> {
    try {
      await api.post('/transactions/validate', transactionData);
      return { valid: true };
    } catch (error) {
      if (error instanceof AxiosError) {
        const errors = error.response?.data?.detail || ['Invalid transaction data'];
        return { valid: false, errors: Array.isArray(errors) ? errors : [errors] };
      }
      return { valid: false, errors: ['Unknown validation error'] };
    }
  }

  async exportTransactions(
    format: 'csv' | 'xlsx' | 'pdf',
    filters?: TransactionFilters
  ): Promise<Blob> {
    const params = new URLSearchParams({ format });

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }

    const response = await api.get(`/transactions/export?${params.toString()}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async importTransactions(file: File, format: 'csv' | 'xlsx'): Promise<{ success: number; errors: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', format);

    const response = await api.post('/transactions/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

// Create and export singleton instance
const transactionsService = new TransactionsService();
export default transactionsService;

// Export service class for testing
export { TransactionsService };