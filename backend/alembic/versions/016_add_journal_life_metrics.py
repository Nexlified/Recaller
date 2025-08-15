"""Add day quality and life metrics to journal entries

Revision ID: 016_add_journal_life_metrics
Revises: 015_add_family_information
Create Date: 2025-01-15 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016_add_journal_life_metrics'
down_revision = '015_add_family_information'
branch_labels = None
depends_on = None


def upgrade():
    # Add new life metrics fields to journal_entries table
    op.add_column('journal_entries', sa.Column('day_quality_rating', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('energy_level', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('stress_level', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('productivity_level', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('social_interactions_count', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('exercise_minutes', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('sleep_quality', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('weather_impact', sa.String(length=20), nullable=True))
    op.add_column('journal_entries', sa.Column('significant_events', sa.JSON(), nullable=True))
    
    # Add indexes for performance on commonly filtered fields
    op.create_index('ix_journal_entries_day_quality_rating', 'journal_entries', ['day_quality_rating'])
    op.create_index('ix_journal_entries_energy_level', 'journal_entries', ['energy_level'])
    op.create_index('ix_journal_entries_weather_impact', 'journal_entries', ['weather_impact'])
    
    # Add check constraints for rating fields (1-10 scale)
    op.create_check_constraint(
        'ck_journal_entries_day_quality_rating_range',
        'journal_entries',
        'day_quality_rating IS NULL OR (day_quality_rating >= 1 AND day_quality_rating <= 10)'
    )
    op.create_check_constraint(
        'ck_journal_entries_energy_level_range',
        'journal_entries',
        'energy_level IS NULL OR (energy_level >= 1 AND energy_level <= 10)'
    )
    op.create_check_constraint(
        'ck_journal_entries_stress_level_range',
        'journal_entries',
        'stress_level IS NULL OR (stress_level >= 1 AND stress_level <= 10)'
    )
    op.create_check_constraint(
        'ck_journal_entries_productivity_level_range',
        'journal_entries',
        'productivity_level IS NULL OR (productivity_level >= 1 AND productivity_level <= 10)'
    )
    op.create_check_constraint(
        'ck_journal_entries_sleep_quality_range',
        'journal_entries',
        'sleep_quality IS NULL OR (sleep_quality >= 1 AND sleep_quality <= 10)'
    )
    
    # Add check constraints for positive values
    op.create_check_constraint(
        'ck_journal_entries_social_interactions_count_positive',
        'journal_entries',
        'social_interactions_count IS NULL OR social_interactions_count >= 0'
    )
    op.create_check_constraint(
        'ck_journal_entries_exercise_minutes_positive',
        'journal_entries',
        'exercise_minutes IS NULL OR exercise_minutes >= 0'
    )
    
    # Add check constraint for weather_impact values
    op.create_check_constraint(
        'ck_journal_entries_weather_impact_values',
        'journal_entries',
        "weather_impact IS NULL OR weather_impact IN ('positive', 'neutral', 'negative')"
    )


def downgrade():
    # Remove check constraints
    op.drop_constraint('ck_journal_entries_weather_impact_values', 'journal_entries')
    op.drop_constraint('ck_journal_entries_exercise_minutes_positive', 'journal_entries')
    op.drop_constraint('ck_journal_entries_social_interactions_count_positive', 'journal_entries')
    op.drop_constraint('ck_journal_entries_sleep_quality_range', 'journal_entries')
    op.drop_constraint('ck_journal_entries_productivity_level_range', 'journal_entries')
    op.drop_constraint('ck_journal_entries_stress_level_range', 'journal_entries')
    op.drop_constraint('ck_journal_entries_energy_level_range', 'journal_entries')
    op.drop_constraint('ck_journal_entries_day_quality_rating_range', 'journal_entries')
    
    # Remove indexes
    op.drop_index('ix_journal_entries_weather_impact', table_name='journal_entries')
    op.drop_index('ix_journal_entries_energy_level', table_name='journal_entries')
    op.drop_index('ix_journal_entries_day_quality_rating', table_name='journal_entries')
    
    # Remove columns
    op.drop_column('journal_entries', 'significant_events')
    op.drop_column('journal_entries', 'weather_impact')
    op.drop_column('journal_entries', 'sleep_quality')
    op.drop_column('journal_entries', 'exercise_minutes')
    op.drop_column('journal_entries', 'social_interactions_count')
    op.drop_column('journal_entries', 'productivity_level')
    op.drop_column('journal_entries', 'stress_level')
    op.drop_column('journal_entries', 'energy_level')
    op.drop_column('journal_entries', 'day_quality_rating')