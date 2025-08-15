"""Import currencies from YAML configuration

Revision ID: 018_import_currencies
Revises: 017_create_currencies_table
Create Date: 2025-08-15 18:08:56.721804

"""
from alembic import op
import sqlalchemy as sa
import yaml
from pathlib import Path
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '018_import_currencies'
down_revision = '017_create_currencies_table'
branch_labels = None
depends_on = None


def load_currencies_config():
    """Load currencies from YAML configuration"""
    # Get the path relative to the backend directory
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "currencies.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Currency configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def upgrade() -> None:
    # Import currencies from YAML configuration
    try:
        config = load_currencies_config()
        currencies_data = config['currencies']
        
        # Get connection and table metadata
        connection = op.get_bind()
        currencies_table = sa.table(
            'currencies',
            sa.column('code', sa.String(3)),
            sa.column('name', sa.String(100)),
            sa.column('symbol', sa.String(10)),
            sa.column('decimal_places', sa.Integer),
            sa.column('is_active', sa.Boolean),
            sa.column('is_default', sa.Boolean),
            sa.column('country_codes', postgresql.ARRAY(sa.String(2)))
        )
        
        # Prepare currency data for bulk insert
        currency_rows = []
        for currency_info in currencies_data:
            currency_rows.append({
                'code': currency_info['code'],
                'name': currency_info['name'],
                'symbol': currency_info['symbol'],
                'decimal_places': currency_info['decimal_places'],
                'country_codes': currency_info.get('countries', []),
                'is_active': currency_info['is_active'],
                'is_default': currency_info.get('is_default', False)
            })
        
        # Insert currencies in batch
        if currency_rows:
            op.bulk_insert(currencies_table, currency_rows)
            print(f"Imported {len(currency_rows)} currencies from YAML configuration")
        
    except Exception as e:
        print(f"Warning: Could not import currencies from YAML: {e}")
        print("You can manually run 'python scripts/import_currencies.py' after migration")


def downgrade() -> None:
    # Remove all currencies that were imported
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM currencies"))
    print("Removed all currencies from database")
