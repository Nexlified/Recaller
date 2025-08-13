"""Create financial transactions tables

Revision ID: 010_create_financial_tables
Revises: 009_create_tasks
Create Date: 2025-08-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = '010_create_financial_tables'
down_revision = '009_create_tasks'
branch_labels = None
depends_on = None

def upgrade():
    # Financial Accounts table
    op.create_table(
        'financial_accounts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('account_name', sa.String(100), nullable=False),
        sa.Column('account_type', sa.String(50), nullable=True),  # checking, savings, credit_card, investment
        sa.Column('account_number', sa.String(50), nullable=True),
        sa.Column('bank_name', sa.String(100), nullable=True),
        sa.Column('current_balance', sa.Numeric(15, 2), default=0),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Transaction Categories table
    op.create_table(
        'transaction_categories',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),  # null for system categories
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=True),  # income, expense, transfer
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('is_system', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    # Transaction Subcategories table
    op.create_table(
        'transaction_subcategories',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('transaction_categories.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('budget_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    # Recurring Transactions table
    op.create_table(
        'recurring_transactions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('template_name', sa.String(200), nullable=False),
        sa.Column('type', sa.String(10), nullable=False),  # credit, debit
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('transaction_categories.id'), nullable=True),
        sa.Column('subcategory_id', sa.Integer, sa.ForeignKey('transaction_subcategories.id'), nullable=True),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('financial_accounts.id'), nullable=True),
        sa.Column('frequency', sa.String(20), nullable=False),  # daily, weekly, monthly, quarterly, yearly
        sa.Column('interval_count', sa.Integer, default=1),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('next_due_date', sa.Date, nullable=True),
        sa.Column('reminder_days', sa.Integer, default=3),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('extra_data', sa.JSON().with_variant(JSONB, "postgresql"), nullable=True),  # EMI details, loan info, etc.
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Main Transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('type', sa.String(10), nullable=False),  # credit, debit
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('transaction_date', sa.Date, nullable=False),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('transaction_categories.id'), nullable=True),
        sa.Column('subcategory_id', sa.Integer, sa.ForeignKey('transaction_subcategories.id'), nullable=True),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('financial_accounts.id'), nullable=True),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('is_recurring', sa.Boolean, default=False),
        sa.Column('recurring_template_id', sa.Integer, sa.ForeignKey('recurring_transactions.id'), nullable=True),
        sa.Column('attachments', sa.JSON().with_variant(JSONB, "postgresql"), nullable=True),
        sa.Column('extra_data', sa.JSON().with_variant(JSONB, "postgresql"), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('transaction_categories.id'), nullable=True),
        sa.Column('subcategory_id', sa.Integer, sa.ForeignKey('transaction_subcategories.id'), nullable=True),
        sa.Column('budget_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('period', sa.String(20), nullable=False),  # monthly, quarterly, yearly
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('alert_percentage', sa.Integer, default=80),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create indexes for better performance
    op.create_index('idx_transactions_user_date', 'transactions', ['user_id', 'transaction_date'])
    op.create_index('idx_transactions_category', 'transactions', ['category_id'])
    op.create_index('idx_transactions_type', 'transactions', ['type'])
    op.create_index('idx_financial_accounts_user', 'financial_accounts', ['user_id'])
    op.create_index('idx_recurring_transactions_next_due', 'recurring_transactions', ['next_due_date'])
    op.create_index('idx_budgets_user_period', 'budgets', ['user_id', 'period'])
    
    # Add check constraints
    op.create_check_constraint(
        'check_transaction_type',
        'transactions',
        "type IN ('credit', 'debit')"
    )
    op.create_check_constraint(
        'check_recurring_transaction_type',
        'recurring_transactions',
        "type IN ('credit', 'debit')"
    )
    op.create_check_constraint(
        'check_category_type',
        'transaction_categories',
        "type IN ('income', 'expense', 'transfer')"
    )

def downgrade():
    op.drop_table('budgets')
    op.drop_table('transactions')
    op.drop_table('recurring_transactions')
    op.drop_table('transaction_subcategories')
    op.drop_table('transaction_categories')
    op.drop_table('financial_accounts')