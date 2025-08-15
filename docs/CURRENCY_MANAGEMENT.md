# Currency Management System

A comprehensive currency management system for Recaller that replaces hardcoded 'USD' defaults with a proper database-driven configuration system.

## Overview

The currency management system provides:

- **Database Storage**: Currencies stored in PostgreSQL with proper indexing
- **YAML Configuration**: Source of truth in `shared/config/reference-data/core/currencies.yml`
- **RESTful API**: Full CRUD operations for currency management
- **Frontend Integration**: Dynamic currency loading in all transaction forms
- **Validation**: Proper ISO 4217 currency code validation
- **Decimal Handling**: Respects currency-specific decimal places (JPY=0, USD=2, etc.)

## Architecture

### Backend Components

```
backend/
├── app/
│   ├── models/currency.py              # SQLAlchemy Currency model
│   ├── schemas/currency.py             # Pydantic schemas
│   ├── crud/currency.py                # CRUD operations
│   ├── api/v1/endpoints/currencies.py  # REST API endpoints
│   └── core/currency_validator.py      # Validation utilities
├── alembic/versions/
│   └── 014_create_currencies_table.py  # Database migration
└── scripts/
    ├── import_currencies.py            # YAML import script
    └── test_currency_integration.py    # Integration tests
```

### Frontend Components

```
frontend/src/
├── services/currencyService.ts         # API client service
└── components/transactions/
    ├── AmountDisplay.tsx               # Currency-aware amount display
    ├── TransactionForm.tsx             # Dynamic currency dropdown
    └── TransactionFilters.tsx          # Currency filtering
```

### Configuration

```
shared/config/reference-data/core/currencies.yml  # Source of truth
```

## Database Schema

```sql
CREATE TABLE currencies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL,           -- ISO 4217 code (USD, EUR, etc.)
    name VARCHAR(100) NOT NULL,                -- Full name (US Dollar, Euro, etc.)
    symbol VARCHAR(10) NOT NULL,               -- Symbol ($, €, £, etc.)
    decimal_places INTEGER NOT NULL DEFAULT 2, -- Decimal places (0 for JPY, 2 for USD)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,   -- Is currency active?
    is_default BOOLEAN NOT NULL DEFAULT FALSE, -- Is default currency?
    country_codes TEXT[],                      -- Associated country codes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX ix_currencies_code ON currencies(code);
CREATE INDEX ix_currencies_is_active ON currencies(is_active);
CREATE INDEX ix_currencies_is_default ON currencies(is_default);
```

## Setup Instructions

### 1. Run Database Migration

```bash
cd backend
alembic upgrade head
```

### 2. Import Currency Data

```bash
cd backend
python scripts/import_currencies.py
```

### 3. Verify Installation

```bash
cd backend  
python scripts/test_currency_integration.py
```

## API Endpoints

### Currency Management

- `GET /api/v1/currencies/` - List all currencies (with filtering)
- `GET /api/v1/currencies/active` - Get only active currencies (for dropdowns)
- `GET /api/v1/currencies/default` - Get the default currency
- `GET /api/v1/currencies/{code}` - Get specific currency by code
- `GET /api/v1/currencies/by-country/{country_code}` - Get currencies by country
- `POST /api/v1/currencies/validate` - Validate currency code
- `POST /api/v1/currencies/` - Create new currency (admin)
- `PUT /api/v1/currencies/{id}` - Update currency (admin)
- `POST /api/v1/currencies/{id}/set-default` - Set default currency (admin)

### Example API Usage

```javascript
// Get active currencies for dropdown
const currencies = await currencyService.getActiveCurrencies();

// Validate currency code
const validation = await currencyService.validateCurrency('USD');

// Format amount with proper currency
const formatted = currencyService.formatAmount(1234.56, currency, true, 'credit');
// Output: "+$1,234.56" (for USD) or "+¥1,235" (for JPY)
```

## Frontend Integration

### Currency Service

```typescript
import { currencyService } from '../services/currencyService';

// Load currencies
const currencies = await currencyService.getActiveCurrencies();

// Format amounts
const formatted = currencyService.formatAmount(amount, currency, showSign, type);
```

### Components

All transaction-related components now:

1. **Load currencies dynamically** from the API
2. **Respect decimal places** (JPY shows no decimals, others show 2)
3. **Display proper symbols** (¥, €, £, $, etc.)
4. **Provide fallbacks** if API is unavailable
5. **Show loading states** during API calls

## Configuration Management

### Adding New Currencies

1. **Update YAML**: Add currency to `shared/config/reference-data/core/currencies.yml`
2. **Re-import**: Run `python scripts/import_currencies.py`
3. **Verify**: Currency appears in all dropdowns automatically

### Currency YAML Format

```yaml
- key: "usd"
  display_name: "US Dollar"
  description: "United States Dollar"
  sort_order: 0
  is_system: true
  is_active: true
  metadata:
    iso_code: "USD"
    symbol: "$"
    numeric_code: "840"
    decimal_places: 2
    countries: ["US"]
  tags: ["currency", "major", "north_america"]
```

## Validation

### Backend Validation

- **ISO 4217 Format**: Exactly 3 alphabetic characters
- **Uppercase Conversion**: Automatic conversion to uppercase
- **Active Check**: Only active currencies allowed in transactions
- **Decimal Places**: Validates against currency's decimal_places setting

### Frontend Validation

- **Format Validation**: Client-side ISO code validation
- **API Validation**: Server-side active currency checking
- **Type Safety**: Full TypeScript interfaces for all currency data

## Migration from Hardcoded Values

The system maintains backward compatibility:

1. **Default Fallback**: USD remains the fallback default
2. **Graceful Degradation**: Frontend falls back to hardcoded options if API fails
3. **Existing Data**: All existing transactions continue to work
4. **Progressive Enhancement**: New features use dynamic currencies

## Testing

### Unit Tests

```bash
cd backend
pytest tests/test_currency_crud.py
pytest tests/test_currency_schemas.py
pytest tests/test_currency_import.py
```

### Integration Tests

```bash
cd backend
python scripts/test_currency_integration.py
```

### Manual Testing

1. **Create Transaction**: Verify currency dropdown loads dynamically
2. **View Amounts**: Check proper symbols and decimal places
3. **Filter Transactions**: Verify currency filter uses real data
4. **Import Script**: Run import and verify data appears

## Performance Considerations

- **Indexing**: Proper database indexes for fast lookups
- **Caching**: Frontend components cache currency data
- **Lazy Loading**: Currencies loaded only when needed
- **Fallbacks**: Hardcoded fallbacks prevent UI blocking

## Security

- **Validation**: All currency codes validated server-side
- **Tenant Isolation**: Currency data is global (not tenant-specific)
- **Input Sanitization**: Proper validation prevents injection
- **Error Handling**: Graceful handling of invalid currencies

## Future Enhancements

- **Exchange Rates**: Integration with currency conversion APIs
- **Historical Rates**: Track exchange rate changes over time
- **Multi-Currency Accounts**: Support for accounts with multiple currencies
- **Currency Preferences**: User/tenant-specific default currencies
- **Admin Interface**: Web UI for currency management
- **Audit Logging**: Track currency configuration changes

## Troubleshooting

### Common Issues

1. **Import Fails**: Check YAML file path and format
2. **No Currencies in Dropdown**: Verify API endpoint is accessible
3. **Wrong Decimal Places**: Check currency.decimal_places in database
4. **Default Currency Issues**: Ensure exactly one currency has is_default=true

### Debug Commands

```bash
# Check database currencies
psql -d recaller -c "SELECT code, name, is_active, is_default FROM currencies;"

# Test API endpoint
curl http://localhost:8000/api/v1/currencies/active

# Validate import
python scripts/test_currency_integration.py
```