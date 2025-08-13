# Financial Management System

The Financial Management System is a comprehensive module in Recaller that enables users to track their income, expenses, and financial goals with advanced features like recurring transactions, budgets, and analytics.

## 🎯 Overview

The financial management system provides:
- **Transaction Tracking**: Record all credit and debit transactions
- **Account Management**: Manage multiple financial accounts (bank, credit card, cash, etc.)
- **Categorization**: Organize transactions with categories and subcategories
- **Recurring Transactions**: Automate EMIs, salary, subscriptions, and other recurring payments
- **Budget Management**: Set spending limits and track progress
- **Multi-Currency Support**: Handle international transactions
- **Financial Analytics**: Insights, trends, and reporting

## 🗄️ Database Schema

The financial system uses 6 main database tables:

### 1. Transactions Table
Main transaction records with full audit trail.

```sql
transactions:
- id (Primary Key)
- user_id (Foreign Key to users)
- tenant_id (Foreign Key to tenants)
- type (credit/debit)
- amount (Decimal)
- currency (String, default USD)
- description (Text)
- transaction_date (Date)
- category_id (Foreign Key, optional)
- subcategory_id (Foreign Key, optional)
- account_id (Foreign Key, optional)
- is_recurring (Boolean)
- recurring_template_id (Foreign Key, optional)
- metadata (JSONB for flexible data)
- created_at, updated_at (Timestamps)
```

### 2. Financial Accounts Table
User's financial accounts (bank, credit card, cash, etc.)

```sql
financial_accounts:
- id (Primary Key)
- user_id (Foreign Key)
- tenant_id (Foreign Key)
- name (String)
- account_type (bank/credit_card/cash/investment/other)
- account_number (String, optional, encrypted)
- bank_name (String, optional)
- current_balance (Decimal)
- currency (String, default USD)
- is_active (Boolean, default True)
- metadata (JSONB)
- created_at, updated_at (Timestamps)
```

### 3. Transaction Categories Table
Main categories for organizing transactions.

```sql
transaction_categories:
- id (Primary Key)
- user_id (Foreign Key, optional for system categories)
- tenant_id (Foreign Key)
- name (String)
- description (Text, optional)
- color (String, for UI)
- icon (String, for UI)
- is_system (Boolean, for default categories)
- is_active (Boolean)
- created_at, updated_at (Timestamps)
```

### 4. Transaction Subcategories Table
Detailed subcategories under main categories.

```sql
transaction_subcategories:
- id (Primary Key)
- category_id (Foreign Key to transaction_categories)
- user_id (Foreign Key)
- tenant_id (Foreign Key)
- name (String)
- description (Text, optional)
- is_active (Boolean)
- created_at, updated_at (Timestamps)
```

### 5. Recurring Transactions Table
Templates for automated recurring transactions.

```sql
recurring_transactions:
- id (Primary Key)
- user_id (Foreign Key)
- tenant_id (Foreign Key)
- type (credit/debit)
- amount (Decimal)
- currency (String)
- description (Text)
- frequency (daily/weekly/monthly/quarterly/yearly)
- interval_count (Integer, default 1)
- start_date (Date)
- end_date (Date, optional)
- next_due_date (Date)
- last_processed_date (Date, optional)
- category_id (Foreign Key, optional)
- subcategory_id (Foreign Key, optional)
- account_id (Foreign Key, optional)
- is_active (Boolean)
- max_occurrences (Integer, optional)
- occurrence_count (Integer, default 0)
- metadata (JSONB)
- created_at, updated_at (Timestamps)
```

### 6. Budgets Table
Budget management and tracking.

```sql
budgets:
- id (Primary Key)
- user_id (Foreign Key)
- tenant_id (Foreign Key)
- name (String)
- category_id (Foreign Key, optional)
- subcategory_id (Foreign Key, optional)
- amount (Decimal)
- currency (String)
- period (monthly/quarterly/yearly)
- start_date (Date)
- end_date (Date)
- is_active (Boolean)
- alert_threshold (Decimal, 0.0-1.0)
- created_at, updated_at (Timestamps)
```

## 🔗 API Endpoints

### Transaction Management
- `POST /api/v1/transactions/` - Create new transaction
- `GET /api/v1/transactions/` - List transactions with filtering
- `GET /api/v1/transactions/{id}` - Get transaction details
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `POST /api/v1/transactions/bulk` - Bulk create transactions
- `GET /api/v1/transactions/summary/monthly` - Monthly summary
- `GET /api/v1/transactions/analytics/category-breakdown` - Category analysis

### Financial Accounts
- `POST /api/v1/financial-accounts/` - Create account
- `GET /api/v1/financial-accounts/` - List accounts with summaries
- `GET /api/v1/financial-accounts/{id}` - Get account details
- `PUT /api/v1/financial-accounts/{id}` - Update account
- `DELETE /api/v1/financial-accounts/{id}` - Delete account

### Recurring Transactions
- `POST /api/v1/recurring-transactions/` - Create recurring transaction
- `GET /api/v1/recurring-transactions/` - List recurring transactions
- `GET /api/v1/recurring-transactions/due-reminders` - Get due reminders
- `POST /api/v1/recurring-transactions/{id}/generate-transaction` - Generate transaction
- `POST /api/v1/recurring-transactions/process-all-due` - Process all due

### Budget Management
- `POST /api/v1/budgets/` - Create budget
- `GET /api/v1/budgets/` - List budgets with summaries
- `GET /api/v1/budgets/alerts` - Get budget alerts

### Financial Analytics
- `GET /api/v1/financial-analytics/dashboard-summary` - Dashboard overview
- `GET /api/v1/financial-analytics/cash-flow` - Cash flow analysis
- `GET /api/v1/financial-analytics/spending-trends` - Spending trends
- `GET /api/v1/financial-analytics/net-worth` - Net worth tracking
- `GET /api/v1/financial-analytics/category-analysis` - Category breakdown

## ⚙️ Background Processing

### Automated Recurring Transactions
The system automatically processes recurring transactions using Celery background tasks:

- **Daily Processing**: Runs at 6 AM UTC to generate due transactions
- **Email Reminders**: Sent at 8 AM UTC for upcoming payments
- **Configurable Schedules**: 7, 3, 1 days before due date and on due date
- **Error Handling**: Comprehensive retry mechanisms and failure tracking

### Background Task Endpoints
- `POST /api/v1/background-tasks/recurring-transactions/process` - Trigger user processing
- `POST /api/v1/background-tasks/recurring-transactions/send-reminders` - Send reminders
- `GET /api/v1/background-tasks/tasks/{task_id}/status` - Check task status

## 💰 Key Features

### Transaction Management
- **Flexible Recording**: Support for all types of financial transactions
- **Account Integration**: Link transactions to specific accounts with automatic balance updates
- **Categorization**: Organize transactions with custom categories and subcategories
- **Bulk Import**: Import transactions from CSV files or bank exports
- **Search & Filter**: Advanced filtering by date, amount, category, account, and text search

### Recurring Transactions (EMIs, Salary, Subscriptions)
- **Flexible Frequencies**: Daily, weekly, monthly, quarterly, yearly with custom intervals
- **Smart Date Handling**: Handles edge cases like month-end dates and leap years
- **Automated Processing**: Background service generates transactions on due dates
- **Email Notifications**: Reminders sent before due dates
- **Occurrence Limits**: Set maximum number of occurrences
- **Template Management**: Reusable templates for common recurring transactions

### Budget Management
- **Category Budgets**: Set spending limits for specific categories
- **Period Flexibility**: Monthly, quarterly, or yearly budget periods
- **Alert System**: Configurable alerts when approaching budget limits
- **Progress Tracking**: Real-time budget vs. actual spending comparison
- **Visual Indicators**: Color-coded progress indicators

### Multi-Currency Support
- **Global Transactions**: Record transactions in any currency
- **Account Currencies**: Each account can have its own base currency
- **Conversion Tracking**: Track exchange rates and conversion costs
- **Reporting**: Currency-specific and consolidated reporting

### Financial Analytics
- **Dashboard Overview**: Key metrics and trends at a glance
- **Cash Flow Analysis**: Income vs. expenses over time
- **Spending Trends**: Identify patterns and seasonal variations
- **Category Breakdown**: Detailed analysis by transaction categories
- **Net Worth Tracking**: Total assets and liabilities overview

## 🔐 Security & Privacy

### Multi-Tenant Architecture
- **Data Isolation**: Complete separation of data between tenants
- **API Security**: All endpoints validate tenant context
- **Background Tasks**: Tenant-aware processing and notifications

### Data Protection
- **Encryption**: Sensitive account information encrypted at rest
- **Access Control**: Users can only access their own data within their tenant
- **Audit Trail**: Complete transaction history with timestamps
- **Privacy-First**: No data shared with third-party services

## 🚀 Implementation Status

### Completed Features ✅
- Database schema and migrations
- SQLAlchemy models with relationships
- Pydantic schemas with validation
- CRUD operations with advanced filtering
- Complete REST API endpoints
- Background task processing
- Email notification system
- Multi-tenant isolation

### Upcoming Features 🔄
- Frontend React interface
- Data visualization charts
- Mobile responsive design
- Import/export functionality
- Advanced reporting features
- AI-powered insights

## 📚 Related Documentation

- [Database Schema](Database-Schema) - Complete database design
- [API Documentation](API-Documentation) - API endpoints and usage
- [Background Tasks](Background-Tasks) - Automated processing
- [Multi-Tenant Architecture](Multi-Tenant-Architecture) - Tenant management

---

*For implementation details, see GitHub issues [#82](https://github.com/Nexlified/Recaller/issues/82) through [#87](https://github.com/Nexlified/Recaller/issues/87)*