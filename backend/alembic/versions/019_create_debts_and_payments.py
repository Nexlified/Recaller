"""Create personal debts and payments tables

Revision ID: 019_create_debts_and_payments
Revises: 018_import_currencies
Create Date: 2025-08-15 18:49:04.904824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '019_create_debts_and_payments'
down_revision = '018_import_currencies'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create personal_debts table
    op.create_table(
        'personal_debts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('creditor_contact_id', sa.Integer(), nullable=False),
        sa.Column('debtor_contact_id', sa.Integer(), nullable=False),
        sa.Column('debt_type', sa.Enum('personal_loan', 'borrowed_money', 'shared_expense', 'favor_owed', name='debttype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_date', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('active', 'paid', 'forgiven', 'disputed', name='debtstatus'), nullable=False),
        sa.Column('payment_status', sa.Enum('unpaid', 'partial', 'paid', name='paymentstatus'), nullable=False),
        sa.Column('reminder_frequency', sa.Enum('never', 'weekly', 'monthly', name='reminderfrequency'), nullable=False),
        sa.Column('last_reminder_sent', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['creditor_contact_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['debtor_contact_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for personal_debts
    op.create_index(op.f('ix_personal_debts_id'), 'personal_debts', ['id'], unique=False)
    op.create_index(op.f('ix_personal_debts_user_id'), 'personal_debts', ['user_id'], unique=False)
    op.create_index(op.f('ix_personal_debts_tenant_id'), 'personal_debts', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_personal_debts_creditor_contact_id'), 'personal_debts', ['creditor_contact_id'], unique=False)
    op.create_index(op.f('ix_personal_debts_debtor_contact_id'), 'personal_debts', ['debtor_contact_id'], unique=False)
    op.create_index(op.f('ix_personal_debts_debt_type'), 'personal_debts', ['debt_type'], unique=False)
    op.create_index(op.f('ix_personal_debts_due_date'), 'personal_debts', ['due_date'], unique=False)
    op.create_index(op.f('ix_personal_debts_status'), 'personal_debts', ['status'], unique=False)
    op.create_index(op.f('ix_personal_debts_payment_status'), 'personal_debts', ['payment_status'], unique=False)
    
    # Create debt_payments table
    op.create_table(
        'debt_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('debt_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['debt_id'], ['personal_debts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for debt_payments
    op.create_index(op.f('ix_debt_payments_id'), 'debt_payments', ['id'], unique=False)
    op.create_index(op.f('ix_debt_payments_debt_id'), 'debt_payments', ['debt_id'], unique=False)
    op.create_index(op.f('ix_debt_payments_payment_date'), 'debt_payments', ['payment_date'], unique=False)


def downgrade() -> None:
    # Drop debt_payments table first (due to foreign key)
    op.drop_index(op.f('ix_debt_payments_payment_date'), table_name='debt_payments')
    op.drop_index(op.f('ix_debt_payments_debt_id'), table_name='debt_payments')
    op.drop_index(op.f('ix_debt_payments_id'), table_name='debt_payments')
    op.drop_table('debt_payments')
    
    # Drop personal_debts table
    op.drop_index(op.f('ix_personal_debts_payment_status'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_status'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_due_date'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_debt_type'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_debtor_contact_id'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_creditor_contact_id'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_tenant_id'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_user_id'), table_name='personal_debts')
    op.drop_index(op.f('ix_personal_debts_id'), table_name='personal_debts')
    op.drop_table('personal_debts')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS reminderfrequency')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS debtstatus')
    op.execute('DROP TYPE IF EXISTS debttype')
