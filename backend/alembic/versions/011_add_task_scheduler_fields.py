"""Add task scheduler tracking fields

Revision ID: 011_add_task_scheduler_fields
Revises: 010_create_financial_tables
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_add_task_scheduler_fields'
down_revision = '010_create_financial_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add generation tracking fields to task_recurrence table
    op.add_column('task_recurrence', sa.Column('last_generated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('task_recurrence', sa.Column('next_generation_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('task_recurrence', sa.Column('generation_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add parent_task_id to tasks table for tracking recurring task instances
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint for parent_task_id
    op.create_foreign_key(
        'fk_tasks_parent_task_id_tasks',
        'tasks', 'tasks',
        ['parent_task_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add index for parent_task_id for performance
    op.create_index('ix_tasks_parent_task_id', 'tasks', ['parent_task_id'])


def downgrade():
    # Remove index and foreign key constraint
    op.drop_index('ix_tasks_parent_task_id', 'tasks')
    op.drop_constraint('fk_tasks_parent_task_id_tasks', 'tasks', type_='foreignkey')
    
    # Remove parent_task_id column
    op.drop_column('tasks', 'parent_task_id')
    
    # Remove generation tracking fields from task_recurrence table
    op.drop_column('task_recurrence', 'generation_count')
    op.drop_column('task_recurrence', 'next_generation_at')
    op.drop_column('task_recurrence', 'last_generated_at')