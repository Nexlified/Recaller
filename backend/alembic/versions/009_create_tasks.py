"""Create tasks tables

Revision ID: 009_create_tasks
Revises: 008_add_contact_visibility
Create Date: 2025-08-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_create_tasks'
down_revision = '008_add_contact_visibility'
branch_labels = None
depends_on = None


def upgrade():
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Basic Information
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Status and Priority
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('priority', sa.String(10), nullable=False, server_default='medium'),
        
        # Dates
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Recurrence
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_tasks_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_tasks_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_tenant_id_user_id'), 'tasks', ['tenant_id', 'user_id'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    op.create_index(op.f('ix_tasks_due_date'), 'tasks', ['due_date'], unique=False)
    op.create_index(op.f('ix_tasks_priority'), 'tasks', ['priority'], unique=False)

    # Create task_contacts junction table
    op.create_table(
        'task_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('relationship_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_contacts_task_id_tasks'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_task_contacts_contact_id_contacts'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'contact_id', name='uq_task_contacts_task_contact')
    )
    op.create_index(op.f('ix_task_contacts_id'), 'task_contacts', ['id'], unique=False)
    op.create_index(op.f('ix_task_contacts_task_id'), 'task_contacts', ['task_id'], unique=False)
    op.create_index(op.f('ix_task_contacts_contact_id'), 'task_contacts', ['contact_id'], unique=False)

    # Create task_recurrence table
    op.create_table(
        'task_recurrence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        
        # Recurrence Pattern
        sa.Column('recurrence_type', sa.String(20), nullable=False),
        sa.Column('recurrence_interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('days_of_week', sa.String(7), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        
        # End conditions
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('max_occurrences', sa.Integer(), nullable=True),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, server_default='0'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_recurrence_task_id_tasks'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_recurrence_id'), 'task_recurrence', ['id'], unique=False)
    op.create_index(op.f('ix_task_recurrence_task_id'), 'task_recurrence', ['task_id'], unique=False)

    # Create task_categories table
    op.create_table(
        'task_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Basic Information
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_task_categories_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_task_categories_user_id_users')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'user_id', 'name', name='uq_task_categories_tenant_user_name')
    )
    op.create_index(op.f('ix_task_categories_id'), 'task_categories', ['id'], unique=False)
    op.create_index(op.f('ix_task_categories_tenant_id_user_id'), 'task_categories', ['tenant_id', 'user_id'], unique=False)

    # Create task_category_assignments junction table
    op.create_table(
        'task_category_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_category_assignments_task_id_tasks'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['task_categories.id'], name=op.f('fk_task_category_assignments_category_id_task_categories'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'category_id', name='uq_task_category_assignments_task_category')
    )
    op.create_index(op.f('ix_task_category_assignments_id'), 'task_category_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_task_category_assignments_task_id'), 'task_category_assignments', ['task_id'], unique=False)
    op.create_index(op.f('ix_task_category_assignments_category_id'), 'task_category_assignments', ['category_id'], unique=False)


def downgrade():
    # Drop tables in reverse order due to foreign key dependencies
    op.drop_index(op.f('ix_task_category_assignments_category_id'), table_name='task_category_assignments')
    op.drop_index(op.f('ix_task_category_assignments_task_id'), table_name='task_category_assignments')
    op.drop_index(op.f('ix_task_category_assignments_id'), table_name='task_category_assignments')
    op.drop_table('task_category_assignments')
    
    op.drop_index(op.f('ix_task_categories_tenant_id_user_id'), table_name='task_categories')
    op.drop_index(op.f('ix_task_categories_id'), table_name='task_categories')
    op.drop_table('task_categories')
    
    op.drop_index(op.f('ix_task_recurrence_task_id'), table_name='task_recurrence')
    op.drop_index(op.f('ix_task_recurrence_id'), table_name='task_recurrence')
    op.drop_table('task_recurrence')
    
    op.drop_index(op.f('ix_task_contacts_contact_id'), table_name='task_contacts')
    op.drop_index(op.f('ix_task_contacts_task_id'), table_name='task_contacts')
    op.drop_index(op.f('ix_task_contacts_id'), table_name='task_contacts')
    op.drop_table('task_contacts')
    
    op.drop_index(op.f('ix_tasks_priority'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_due_date'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_tenant_id_user_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')