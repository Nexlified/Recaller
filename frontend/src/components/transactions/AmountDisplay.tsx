'use client';

import React from 'react';

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
  const formatAmount = (amount: number, currency: string): string => {
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency.toUpperCase(),
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(Math.abs(amount));
    } catch {
      // Fallback for unsupported currencies
      return `${currency.toUpperCase()} ${Math.abs(amount).toFixed(2)}`;
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

  const formattedAmount = formatAmount(amount, currency);
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