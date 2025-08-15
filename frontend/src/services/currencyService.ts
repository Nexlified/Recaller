import { api } from './api';

export interface Currency {
  id: number;
  code: string;
  name: string;
  symbol: string;
  decimal_places: number;
  is_active: boolean;
  is_default: boolean;
  country_codes: string[];
  created_at: string;
  updated_at: string;
}

export interface CurrencyList {
  currencies: Currency[];
  total: number;
  active_count: number;
  default_currency: Currency | null;
}

export interface CurrencyValidation {
  currency_code: string;
  is_valid: boolean;
}

class CurrencyService {
  /**
   * Get all currencies (with optional filtering)
   */
  async getCurrencies(activeOnly: boolean = false): Promise<CurrencyList> {
    const response = await api.get('/currencies/', {
      params: { active_only: activeOnly }
    });
    return response.data;
  }

  /**
   * Get only active currencies (optimized for dropdowns)
   */
  async getActiveCurrencies(): Promise<Currency[]> {
    const response = await api.get('/currencies/active');
    return response.data;
  }

  /**
   * Get the default currency
   */
  async getDefaultCurrency(): Promise<Currency | null> {
    const response = await api.get('/currencies/default');
    return response.data;
  }

  /**
   * Get a specific currency by code
   */
  async getCurrencyByCode(code: string): Promise<Currency> {
    const response = await api.get(`/currencies/${code}`);
    return response.data;
  }

  /**
   * Get currencies used in a specific country
   */
  async getCurrenciesByCountry(countryCode: string): Promise<Currency[]> {
    const response = await api.get(`/currencies/by-country/${countryCode}`);
    return response.data;
  }

  /**
   * Validate a currency code
   */
  async validateCurrency(code: string): Promise<CurrencyValidation> {
    const response = await api.post('/currencies/validate', null, {
      params: { currency_code: code }
    });
    return response.data;
  }

  /**
   * Create a new currency (admin functionality)
   */
  async createCurrency(currency: Partial<Currency>): Promise<Currency> {
    const response = await api.post('/currencies/', currency);
    return response.data;
  }

  /**
   * Update an existing currency (admin functionality)
   */
  async updateCurrency(id: number, updates: Partial<Currency>): Promise<Currency> {
    const response = await api.put(`/currencies/${id}`, updates);
    return response.data;
  }

  /**
   * Set a currency as default (admin functionality)
   */
  async setDefaultCurrency(id: number): Promise<Currency> {
    const response = await api.post(`/currencies/${id}/set-default`);
    return response.data;
  }

  /**
   * Format an amount using currency information
   */
  formatAmount(amount: number, currency: Currency, showSign?: boolean, type?: 'credit' | 'debit'): string {
    try {
      const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency.code,
        minimumFractionDigits: currency.decimal_places,
        maximumFractionDigits: currency.decimal_places,
      });
      
      let formattedAmount = formatter.format(Math.abs(amount));
      
      // Add sign prefix if requested
      if (showSign && type) {
        const prefix = type === 'credit' ? '+' : '-';
        formattedAmount = prefix + formattedAmount;
      }
      
      return formattedAmount;
    } catch {
      // Fallback for unsupported currencies
      const sign = showSign && type ? (type === 'credit' ? '+' : '-') : '';
      return `${sign}${currency.symbol}${Math.abs(amount).toFixed(currency.decimal_places)}`;
    }
  }

  /**
   * Get currency symbol by code (with fallback)
   */
  getCurrencySymbol(currencies: Currency[], code: string): string {
    const currency = currencies.find(c => c.code === code);
    return currency?.symbol || code;
  }
}

// Export singleton instance
export const currencyService = new CurrencyService();
export default currencyService;