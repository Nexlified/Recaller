'use client';

import React, { useState, useEffect } from 'react';
import { Currency, currencyService } from '../../services/currencyService';

interface AmountDisplayProps {
  amount: number;
  currency?: string;
  type?: 'credit' | 'debit';
  showSign?: boolean;
  className?: string;
}

export const AmountDisplay: React.FC<AmountDisplayProps> = ({ 
  amount, 
  currency = 'USD', 
  type,
  showSign = true,
  className = '' 
}) => {
  const [currencyData, setCurrencyData] = useState<Currency | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCurrencyData = async () => {
      if (!currency) return;
      
      setLoading(true);
      try {
        const data = await currencyService.getCurrencyByCode(currency);
        setCurrencyData(data);
      } catch (error) {
        console.warn(`Failed to fetch currency data for ${currency}:`, error);
        // Set fallback currency data
        setCurrencyData({
          id: 0,
          code: currency.toUpperCase(),
          name: currency.toUpperCase(),
          symbol: currency.toUpperCase(),
          decimal_places: 2,
          is_active: true,
          is_default: false,
          country_codes: [],
          created_at: '',
          updated_at: ''
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCurrencyData();
  }, [currency]);

  const formatAmount = (amount: number, currencyData: Currency): string => {
    if (!currencyData) {
      return `${currency} ${amount.toFixed(2)}`;
    }

    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currencyData.code,
        minimumFractionDigits: currencyData.decimal_places,
        maximumFractionDigits: currencyData.decimal_places,
      }).format(Math.abs(amount));
    } catch {
      // Fallback for unsupported currencies
      return `${currencyData.symbol} ${Math.abs(amount).toFixed(currencyData.decimal_places)}`;
    }
  };

  const getColorClasses = (type?: 'credit' | 'debit'): string => {
    if (!type) return '';
    
    switch (type) {
      case 'credit':
        return 'text-green-600 dark:text-green-400';
      case 'debit':
        return 'text-red-600 dark:text-red-400';
      default:
        return '';
    }
  };

  const getSignPrefix = (type?: 'credit' | 'debit'): string => {
    if (!showSign || !type) return '';
    
    switch (type) {
      case 'credit': return '+';
      case 'debit': return '-';
      default: return '';
    }
  };

  if (loading || !currencyData) {
    return (
      <span className={`font-medium ${className}`}>
        {currency} {amount.toFixed(2)}
      </span>
    );
  }

  const formattedAmount = formatAmount(amount, currencyData);
  const signPrefix = getSignPrefix(type);
  const colorClasses = getColorClasses(type);

  return (
    <span 
      className={`font-medium ${colorClasses} ${className}`}
      aria-label={`Amount: ${signPrefix}${formattedAmount}${type ? ` (${type})` : ''}`}
    >
      {signPrefix && <span aria-hidden="true">{signPrefix}</span>}
      {formattedAmount}
    </span>
  );
};