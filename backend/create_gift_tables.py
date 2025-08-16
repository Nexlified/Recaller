#!/usr/bin/env python3
"""
Create gift tables in SQLite for testing
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, ForeignKey, text, Date, JSON, Numeric
from sqlalchemy.sql import func

def create_gift_tables():
    """Create gift tables in SQLite database"""
    try:
        # Connect to the existing test database
        engine = create_engine("sqlite:///./recaller_test.db", connect_args={"check_same_thread": False})
        
        metadata = MetaData()
        
        # Create gifts table
        gifts_table = Table(
            'gifts', metadata,
            Column('id', Integer, primary_key=True),
            Column('tenant_id', Integer, nullable=False),  # No FK constraint for SQLite
            Column('user_id', Integer, nullable=False),  # No FK constraint for SQLite
            
            # Basic Information
            Column('title', String(255), nullable=False),
            Column('description', String),  # TEXT
            Column('category', String(100)),
            
            # Recipient Information
            Column('recipient_contact_id', Integer),  # Simplified FK
            Column('recipient_name', String(255)),
            
            # Occasion and Timing
            Column('occasion', String(100)),
            Column('occasion_date', Date),
            
            # Financial Information
            Column('budget_amount', Numeric(10, 2)),
            Column('actual_amount', Numeric(10, 2)),
            Column('currency', String(3), nullable=False, default='USD'),
            
            # Status and Priority
            Column('status', String(20), nullable=False, default='idea'),
            Column('priority', Integer, nullable=False, default=2),
            
            # Purchase Information
            Column('store_name', String(255)),
            Column('purchase_url', String),  # TEXT
            Column('purchase_date', Date),
            
            # Gift Details (JSON format)
            Column('gift_details', String, nullable=False, default='{}'),  # JSON as STRING in SQLite
            
            # Tracking Information
            Column('tracking_number', String(255)),
            Column('delivery_date', Date),
            
            # Notes and References
            Column('notes', String),  # TEXT
            Column('image_url', String),  # TEXT
            
            # Reminders and Notifications (JSON format)
            Column('reminder_dates', String, nullable=False, default='{}'),  # JSON as STRING
            
            # Integration References
            Column('task_id', Integer),
            Column('transaction_id', Integer),
            
            # Status
            Column('is_active', Boolean, nullable=False, default=True),
            Column('is_surprise', Boolean, nullable=False, default=False),
            
            # Timestamps
            Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
            Column('updated_at', DateTime(timezone=True))
        )
        
        # Create gift_ideas table
        gift_ideas_table = Table(
            'gift_ideas', metadata,
            Column('id', Integer, primary_key=True),
            Column('tenant_id', Integer, nullable=False),  # No FK constraint for SQLite
            Column('user_id', Integer, nullable=False),  # No FK constraint for SQLite
            
            # Basic Information
            Column('title', String(255), nullable=False),
            Column('description', String),  # TEXT
            Column('category', String(100)),
            
            # Target Information
            Column('target_contact_id', Integer),  # Simplified FK
            Column('target_demographic', String(100)),
            
            # Occasion Context
            Column('suitable_occasions', String, nullable=False, default='[]'),  # JSON as STRING
            
            # Financial Information
            Column('price_range_min', Numeric(10, 2)),
            Column('price_range_max', Numeric(10, 2)),
            Column('currency', String(3), nullable=False, default='USD'),
            
            # Idea Details (JSON format)
            Column('idea_details', String, nullable=False, default='{}'),  # JSON as STRING
            
            # Sources and References
            Column('source_url', String),  # TEXT
            Column('source_description', String),  # TEXT
            Column('image_url', String),  # TEXT
            
            # Rating and Feedback
            Column('rating', Integer),
            Column('notes', String),  # TEXT
            
            # Tracking
            Column('times_gifted', Integer, nullable=False, default=0),
            Column('last_gifted_date', Date),
            
            # Tags for searchability (JSON format)
            Column('tags', String, nullable=False, default='[]'),  # JSON as STRING
            
            # Status
            Column('is_active', Boolean, nullable=False, default=True),
            Column('is_favorite', Boolean, nullable=False, default=False),
            
            # Timestamps
            Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
            Column('updated_at', DateTime(timezone=True))
        )
        
        # Create tables
        metadata.create_all(engine)
        print("✅ Gift tables created successfully")
        
        # Add some indexes for better performance
        with engine.connect() as conn:
            # Create basic indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS ix_gifts_tenant_id ON gifts (tenant_id)",
                "CREATE INDEX IF NOT EXISTS ix_gifts_user_id ON gifts (user_id)",
                "CREATE INDEX IF NOT EXISTS ix_gifts_status ON gifts (status)",
                "CREATE INDEX IF NOT EXISTS ix_gifts_category ON gifts (category)",
                "CREATE INDEX IF NOT EXISTS ix_gifts_occasion ON gifts (occasion)",
                "CREATE INDEX IF NOT EXISTS ix_gifts_occasion_date ON gifts (occasion_date)",
                "CREATE INDEX IF NOT EXISTS ix_gifts_is_active ON gifts (is_active)",
                
                "CREATE INDEX IF NOT EXISTS ix_gift_ideas_tenant_id ON gift_ideas (tenant_id)",
                "CREATE INDEX IF NOT EXISTS ix_gift_ideas_user_id ON gift_ideas (user_id)",
                "CREATE INDEX IF NOT EXISTS ix_gift_ideas_category ON gift_ideas (category)",
                "CREATE INDEX IF NOT EXISTS ix_gift_ideas_is_active ON gift_ideas (is_active)",
                "CREATE INDEX IF NOT EXISTS ix_gift_ideas_is_favorite ON gift_ideas (is_favorite)",
                "CREATE INDEX IF NOT EXISTS ix_gift_ideas_rating ON gift_ideas (rating)"
            ]
            
            for index_sql in indexes:
                conn.execute(text(index_sql))
            conn.commit()
            
        print("✅ Indexes created successfully")
            
    except Exception as e:
        print(f"❌ Error creating gift tables: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    print("🎁 Creating gift tables...")
    create_gift_tables()
    print("✅ Gift tables creation complete!")