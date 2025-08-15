"""Optimize journal storage and retrieval

Revision ID: 013_optimize_journal_storage_and_retrieval
Revises: 012_create_journal_tables
Create Date: 2025-08-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013_optimize_journal_storage_and_retrieval'
down_revision = '012_create_journal_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add strategic indexes for common query patterns
    
    # Composite index for search queries (tenant_id, user_id, is_archived)
    # This optimizes queries that filter by user and archived status
    op.create_index('ix_journal_entries_tenant_user_archived', 'journal_entries', 
                   ['tenant_id', 'user_id', 'is_archived'])
    
    # Composite index for mood filtering (tenant_id, user_id, mood, entry_date)
    # This optimizes queries that filter by mood with date ordering
    op.create_index('ix_journal_entries_tenant_user_mood_date', 'journal_entries', 
                   ['tenant_id', 'user_id', 'mood', 'entry_date'])
    
    # Partial index for non-archived entries only (most common queries)
    # PostgreSQL syntax for partial index - will be ignored in SQLite tests
    try:
        op.execute("""
            CREATE INDEX ix_journal_entries_active_entries_date 
            ON journal_entries (tenant_id, user_id, entry_date DESC) 
            WHERE is_archived = false
        """)
    except Exception:
        # Fallback for databases that don't support partial indexes
        op.create_index('ix_journal_entries_active_entries_fallback', 'journal_entries',
                       ['tenant_id', 'user_id', 'entry_date', 'is_archived'])
    
    # Index for full-text search performance on content and title
    # Note: PostgreSQL specific - will add GIN index for better text search
    try:
        op.execute("""
            CREATE INDEX ix_journal_entries_content_search 
            ON journal_entries USING gin(to_tsvector('english', coalesce(title, '') || ' ' || content))
        """)
    except Exception:
        # Fallback for databases without full-text search
        pass
    
    # Optimize tag queries - composite index for tag filtering
    op.create_index('ix_journal_tags_entry_name_composite', 'journal_tags',
                   ['journal_entry_id', 'tag_name'])
    
    # Index for tag-based entry lookups
    op.create_index('ix_journal_tags_name_entry', 'journal_tags',
                   ['tag_name', 'journal_entry_id'])


def downgrade():
    # Remove the indexes in reverse order
    
    try:
        op.drop_index('ix_journal_tags_name_entry', table_name='journal_tags')
    except Exception:
        pass
        
    try:
        op.drop_index('ix_journal_tags_entry_name_composite', table_name='journal_tags')
    except Exception:
        pass
        
    try:
        op.execute("DROP INDEX IF EXISTS ix_journal_entries_content_search")
    except Exception:
        pass
        
    try:
        op.execute("DROP INDEX IF EXISTS ix_journal_entries_active_entries_date")
    except Exception:
        pass
        
    try:
        op.drop_index('ix_journal_entries_active_entries_fallback', table_name='journal_entries')
    except Exception:
        pass
        
    try:
        op.drop_index('ix_journal_entries_tenant_user_mood_date', table_name='journal_entries')
    except Exception:
        pass
        
    try:
        op.drop_index('ix_journal_entries_tenant_user_archived', table_name='journal_entries')
    except Exception:
        pass