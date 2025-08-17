'use client';

import React, { useState, useEffect } from 'react';
import { Gift, GiftBudget, BudgetInsight } from '../../types/Gift';
import giftsService from '../../services/gifts';

interface BudgetTrackerProps {
  gifts?: Gift[];
  period?: 'month' | 'quarter' | 'year' | 'all';
  className?: string;
}

export const BudgetTracker: React.FC<BudgetTrackerProps> = ({
  gifts: propGifts,
  period = 'month',
  className = ''
}) => {
  const [gifts, setGifts] = useState<Gift[]>(propGifts || []);
  const [budgetSummary, setBudgetSummary] = useState<GiftBudget | null>(null);
  const [budgetInsights, setBudgetInsights] = useState<BudgetInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (propGifts) {
      setGifts(propGifts);
      calculateLocalBudget(propGifts);
    } else {
      loadBudgetData();
    }
  }, [propGifts, period]);

  const loadBudgetData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [giftsData, budgetData, insightsData] = await Promise.all([
        giftsService.getGifts(),
        giftsService.getBudgetSummary(period),
        giftsService.getBudgetInsights()
      ]);
      
      setGifts(giftsData);
      setBudgetSummary(budgetData);
      setBudgetInsights(insightsData);
    } catch (err) {
      console.error('Error loading budget data:', err);
      setError('Failed to load budget data');
      // Fallback to local calculation
      if (gifts.length > 0) {
        calculateLocalBudget(gifts);
      }
    } finally {
      setLoading(false);
    }
  };

  const calculateLocalBudget = (giftList: Gift[]) => {
    // Filter gifts by period
    const filteredGifts = filterGiftsByPeriod(giftList, period);
    
    // Calculate totals
    const totalBudget = filteredGifts.reduce((sum, gift) => sum + (gift.budget_amount || 0), 0);
    const spentAmount = filteredGifts
      .filter(gift => gift.actual_amount && gift.status === 'given')
      .reduce((sum, gift) => sum + (gift.actual_amount || 0), 0);
    
    const summary: GiftBudget = {
      total_budget: totalBudget,
      spent_amount: spentAmount,
      remaining_budget: totalBudget - spentAmount,
      currency: 'USD' // Default currency
    };
    
    setBudgetSummary(summary);
    
    // Calculate insights by category
    const categoryInsights = calculateCategoryInsights(filteredGifts);
    setBudgetInsights(categoryInsights);
    
    setLoading(false);
  };

  const filterGiftsByPeriod = (giftList: Gift[], selectedPeriod: string): Gift[] => {
    const now = new Date();
    const startDate = new Date();
    
    switch (selectedPeriod) {
      case 'month':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case 'quarter':
        startDate.setMonth(now.getMonth() - 3);
        break;
      case 'year':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      case 'all':
        return giftList;
    }
    
    return giftList.filter(gift => {
      const giftDate = gift.occasion_date ? new Date(gift.occasion_date) : new Date(gift.created_at);
      return giftDate >= startDate && giftDate <= now;
    });
  };

  const calculateCategoryInsights = (giftList: Gift[]): BudgetInsight[] => {
    const categoryMap = new Map<string, { budgeted: number; spent: number }>();
    
    giftList.forEach(gift => {
      const category = gift.category || 'Uncategorized';
      const current = categoryMap.get(category) || { budgeted: 0, spent: 0 };
      
      current.budgeted += gift.budget_amount || 0;
      if (gift.status === 'given' && gift.actual_amount) {
        current.spent += gift.actual_amount;
      }
      
      categoryMap.set(category, current);
    });
    
    return Array.from(categoryMap.entries()).map(([category, data]) => ({
      category,
      budgeted: data.budgeted,
      spent: data.spent,
      remaining: data.budgeted - data.spent,
      percentage_used: data.budgeted > 0 ? (data.spent / data.budgeted) * 100 : 0
    }));
  };

  const getBudgetStatus = (budgetData: GiftBudget) => {
    if (!budgetData.total_budget) return { status: 'none', color: 'gray' };
    
    const percentageUsed = (budgetData.spent_amount / budgetData.total_budget) * 100;
    
    if (percentageUsed >= 100) return { status: 'over', color: 'red' };
    if (percentageUsed >= 80) return { status: 'warning', color: 'yellow' };
    return { status: 'good', color: 'green' };
  };

  const getProgressBarColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 80) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="space-y-4">
            <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !budgetSummary) {
    return (
      <div className={`bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 ${className}`}>
        <p className="text-red-800 dark:text-red-200">{error}</p>
      </div>
    );
  }

  if (!budgetSummary) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Budget Tracker</h3>
        <p className="text-gray-500 dark:text-gray-400">No budget data available</p>
      </div>
    );
  }

  const budgetStatus = getBudgetStatus(budgetSummary);
  const percentageUsed = budgetSummary.total_budget > 0 
    ? (budgetSummary.spent_amount / budgetSummary.total_budget) * 100 
    : 0;

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Budget Tracker
          </h3>
          <span className="text-sm text-gray-500 dark:text-gray-400 capitalize">
            {period === 'all' ? 'All time' : `Past ${period}`}
          </span>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Budget Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Total Budget</h4>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {giftsService.formatCurrency(budgetSummary.total_budget, budgetSummary.currency)}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Spent</h4>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {giftsService.formatCurrency(budgetSummary.spent_amount, budgetSummary.currency)}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Remaining</h4>
            <p className={`text-2xl font-bold ${
              budgetSummary.remaining_budget >= 0 
                ? 'text-green-600 dark:text-green-400' 
                : 'text-red-600 dark:text-red-400'
            }`}>
              {giftsService.formatCurrency(budgetSummary.remaining_budget, budgetSummary.currency)}
            </p>
          </div>
        </div>

        {/* Budget Progress */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Budget Usage</h4>
            <span className={`text-sm font-medium ${
              budgetStatus.color === 'red' ? 'text-red-600 dark:text-red-400' :
              budgetStatus.color === 'yellow' ? 'text-yellow-600 dark:text-yellow-400' :
              'text-green-600 dark:text-green-400'
            }`}>
              {percentageUsed.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-300 ${getProgressBarColor(percentageUsed)}`}
              style={{ width: `${Math.min(percentageUsed, 100)}%` }}
            ></div>
          </div>
          {budgetStatus.status === 'over' && (
            <p className="text-xs text-red-600 dark:text-red-400 mt-1">
              Budget exceeded by {giftsService.formatCurrency(Math.abs(budgetSummary.remaining_budget), budgetSummary.currency)}
            </p>
          )}
        </div>

        {/* Category Breakdown */}
        {budgetInsights.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Spending by Category
            </h4>
            <div className="space-y-3">
              {budgetInsights
                .sort((a, b) => b.spent - a.spent)
                .slice(0, 5) // Show top 5 categories
                .map(insight => (
                  <div key={insight.category} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {insight.category}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {giftsService.formatCurrency(insight.spent, budgetSummary.currency)} / 
                          {giftsService.formatCurrency(insight.budgeted, budgetSummary.currency)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${getProgressBarColor(insight.percentage_used)}`}
                          style={{ width: `${Math.min(insight.percentage_used, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Budget Alerts */}
        {budgetStatus.status !== 'good' && (
          <div className={`p-4 rounded-lg ${
            budgetStatus.status === 'over' 
              ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
              : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'
          }`}>
            <div className="flex">
              <svg 
                className={`w-5 h-5 mr-2 ${
                  budgetStatus.status === 'over' ? 'text-red-400' : 'text-yellow-400'
                }`} 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <h4 className={`text-sm font-medium ${
                  budgetStatus.status === 'over' 
                    ? 'text-red-800 dark:text-red-200' 
                    : 'text-yellow-800 dark:text-yellow-200'
                }`}>
                  {budgetStatus.status === 'over' ? 'Budget Exceeded' : 'Budget Warning'}
                </h4>
                <p className={`text-sm ${
                  budgetStatus.status === 'over' 
                    ? 'text-red-700 dark:text-red-300' 
                    : 'text-yellow-700 dark:text-yellow-300'
                }`}>
                  {budgetStatus.status === 'over' 
                    ? 'You have exceeded your gift budget. Consider adjusting future spending.'
                    : 'You are approaching your budget limit. Consider reviewing upcoming gift plans.'
                  }
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};