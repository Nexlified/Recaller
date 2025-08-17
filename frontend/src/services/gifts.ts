import api from './api';
import { AxiosError } from 'axios';
import {
  Gift,
  GiftCreate,
  GiftUpdate,
  GiftIdea,
  GiftIdeaCreate,
  GiftIdeaUpdate,
  GiftFilters,
  GiftIdeaFilters,
  GiftStatus,
  GiftPriority,
  GiftAnalytics,
  GiftBudget,
  BudgetInsight,
  GiftCategoryReference,
  GiftOccasionReference,
  GiftBudgetRangeReference
} from '../types/Gift';

class GiftsService {
  // Gift CRUD operations
  async getGifts(skip: number = 0, limit: number = 100, filters?: GiftFilters): Promise<Gift[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    // Add filters to query params
    if (filters) {
      if (filters.status && filters.status.length > 0) {
        filters.status.forEach(status => params.append('status', status));
      }
      if (filters.category && filters.category.length > 0) {
        filters.category.forEach(category => params.append('category', category));
      }
      if (filters.occasion && filters.occasion.length > 0) {
        filters.occasion.forEach(occasion => params.append('occasion', occasion));
      }
      if (filters.recipient_contact_id && filters.recipient_contact_id.length > 0) {
        filters.recipient_contact_id.forEach(id => params.append('recipient_contact_id', id.toString()));
      }
      if (filters.min_budget !== undefined) params.append('min_budget', filters.min_budget.toString());
      if (filters.max_budget !== undefined) params.append('max_budget', filters.max_budget.toString());
      if (filters.currency) params.append('currency', filters.currency);
      if (filters.is_surprise !== undefined) params.append('is_surprise', filters.is_surprise.toString());
      if (filters.search) params.append('search', filters.search);
    }

    const response = await api.get<Gift[]>(`/gifts/?${params.toString()}`);
    return response.data;
  }

  async getGift(giftId: number): Promise<Gift> {
    const response = await api.get<Gift>(`/gifts/${giftId}`);
    return response.data;
  }

  async createGift(giftData: GiftCreate): Promise<Gift> {
    const response = await api.post<Gift>('/gifts/', giftData);
    return response.data;
  }

  async updateGift(giftId: number, giftData: GiftUpdate): Promise<Gift> {
    const response = await api.put<Gift>(`/gifts/${giftId}`, giftData);
    return response.data;
  }

  async deleteGift(giftId: number): Promise<void> {
    await api.delete(`/gifts/${giftId}`);
  }

  // Gift status operations
  async updateGiftStatus(giftId: number, status: GiftStatus): Promise<Gift> {
    const response = await api.put<Gift>(`/gifts/${giftId}/status`, { status });
    return response.data;
  }

  async markGiftGiven(giftId: number): Promise<Gift> {
    return this.updateGiftStatus(giftId, 'given');
  }

  // Gift filtering and search
  async getGiftsByStatus(status: GiftStatus, skip: number = 0, limit: number = 100): Promise<Gift[]> {
    const response = await api.get<Gift[]>(`/gifts/status/${status}?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getGiftsByContact(contactId: number, skip: number = 0, limit: number = 100): Promise<Gift[]> {
    const response = await api.get<Gift[]>(`/contacts/${contactId}/gifts?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getUpcomingOccasions(skip: number = 0, limit: number = 100): Promise<Gift[]> {
    const response = await api.get<Gift[]>(`/gifts/upcoming-occasions?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async searchGifts(query: string, skip: number = 0, limit: number = 100): Promise<Gift[]> {
    const params = new URLSearchParams({
      q: query,
      skip: skip.toString(),
      limit: limit.toString(),
    });

    const response = await api.get<Gift[]>(`/gifts/search/?${params.toString()}`);
    return response.data;
  }

  // Gift Ideas CRUD operations
  async getGiftIdeas(skip: number = 0, limit: number = 100, filters?: GiftIdeaFilters): Promise<GiftIdea[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    // Add filters to query params
    if (filters) {
      if (filters.category && filters.category.length > 0) {
        filters.category.forEach(category => params.append('category', category));
      }
      if (filters.target_contact_id && filters.target_contact_id.length > 0) {
        filters.target_contact_id.forEach(id => params.append('target_contact_id', id.toString()));
      }
      if (filters.min_rating !== undefined) params.append('min_rating', filters.min_rating.toString());
      if (filters.min_price !== undefined) params.append('min_price', filters.min_price.toString());
      if (filters.max_price !== undefined) params.append('max_price', filters.max_price.toString());
      if (filters.currency) params.append('currency', filters.currency);
      if (filters.is_favorite !== undefined) params.append('is_favorite', filters.is_favorite.toString());
      if (filters.search) params.append('search', filters.search);
    }

    const response = await api.get<GiftIdea[]>(`/gift-ideas/?${params.toString()}`);
    return response.data;
  }

  async getGiftIdea(ideaId: number): Promise<GiftIdea> {
    const response = await api.get<GiftIdea>(`/gift-ideas/${ideaId}`);
    return response.data;
  }

  async createGiftIdea(ideaData: GiftIdeaCreate): Promise<GiftIdea> {
    const response = await api.post<GiftIdea>('/gift-ideas/', ideaData);
    return response.data;
  }

  async updateGiftIdea(ideaId: number, ideaData: GiftIdeaUpdate): Promise<GiftIdea> {
    const response = await api.put<GiftIdea>(`/gift-ideas/${ideaId}`, ideaData);
    return response.data;
  }

  async deleteGiftIdea(ideaId: number): Promise<void> {
    await api.delete(`/gift-ideas/${ideaId}`);
  }

  async searchGiftIdeas(query: string, skip: number = 0, limit: number = 100): Promise<GiftIdea[]> {
    const params = new URLSearchParams({
      q: query,
      skip: skip.toString(),
      limit: limit.toString(),
    });

    const response = await api.get<GiftIdea[]>(`/gift-ideas/search/?${params.toString()}`);
    return response.data;
  }

  async convertIdeaToGift(ideaId: number, giftData: Partial<GiftCreate>): Promise<Gift> {
    const response = await api.post<Gift>(`/gift-ideas/${ideaId}/convert-to-gift`, giftData);
    return response.data;
  }

  // Analytics and budget tracking
  async getGiftAnalytics(): Promise<GiftAnalytics> {
    const response = await api.get<GiftAnalytics>('/analytics/');
    return response.data;
  }

  async getBudgetInsights(): Promise<BudgetInsight[]> {
    const response = await api.get<BudgetInsight[]>('/analytics/budget-insights/');
    return response.data;
  }

  async getGiftGivingPatterns(): Promise<Record<string, any>> {
    const response = await api.get<Record<string, any>>('/analytics/gift-patterns/');
    return response.data;
  }

  async getBudgetSummary(period?: string): Promise<GiftBudget> {
    const params = period ? `?period=${period}` : '';
    const response = await api.get<GiftBudget>(`/budget/summary${params}`);
    return response.data;
  }

  // Reference data
  async getGiftCategories(): Promise<GiftCategoryReference[]> {
    const response = await api.get<GiftCategoryReference[]>('/gift-system/reference-data/categories');
    return response.data;
  }

  async getGiftOccasions(): Promise<GiftOccasionReference[]> {
    const response = await api.get<GiftOccasionReference[]>('/gift-system/reference-data/occasions');
    return response.data;
  }

  async getGiftBudgetRanges(): Promise<GiftBudgetRangeReference[]> {
    const response = await api.get<GiftBudgetRangeReference[]>('/gift-system/reference-data/budget-ranges');
    return response.data;
  }

  // Configuration
  async getGiftSystemConfig(): Promise<Record<string, any>> {
    const response = await api.get<Record<string, any>>('/gift-system/config');
    return response.data;
  }

  async getGiftSystemStatus(): Promise<Record<string, any>> {
    const response = await api.get<Record<string, any>>('/gift-system/status');
    return response.data;
  }

  // Utility methods
  isGiftOverdue(gift: Gift): boolean {
    if (!gift.occasion_date || gift.status === 'given') {
      return false;
    }
    return new Date(gift.occasion_date) < new Date();
  }

  getGiftStatusColor(status: GiftStatus): string {
    switch (status) {
      case 'idea': return 'gray';
      case 'planned': return 'blue';
      case 'purchased': return 'yellow';
      case 'wrapped': return 'purple';
      case 'given': return 'green';
      case 'returned': return 'red';
      default: return 'gray';
    }
  }

  getGiftPriorityColor(priority: GiftPriority): string {
    switch (priority) {
      case 1: return 'green';
      case 2: return 'yellow';
      case 3: return 'orange';
      case 4: return 'red';
      default: return 'gray';
    }
  }

  getGiftDisplayName(gift: Gift): string {
    return gift.title.trim() || 'Untitled Gift';
  }

  formatOccasionDate(occasionDate: string): string {
    const date = new Date(occasionDate);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays < 0) return `${Math.abs(diffDays)} days ago`;
    if (diffDays < 7) return `In ${diffDays} days`;
    if (diffDays < 30) return `In ${Math.ceil(diffDays / 7)} weeks`;
    
    return date.toLocaleDateString();
  }

  formatCurrency(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  calculateBudgetUtilization(budget: number, spent: number): {
    percentage: number;
    status: 'under' | 'approaching' | 'over';
    color: string;
  } {
    const percentage = budget > 0 ? (spent / budget) * 100 : 0;
    
    let status: 'under' | 'approaching' | 'over';
    let color: string;
    
    if (percentage < 75) {
      status = 'under';
      color = 'green';
    } else if (percentage < 100) {
      status = 'approaching';
      color = 'yellow';
    } else {
      status = 'over';
      color = 'red';
    }
    
    return { percentage, status, color };
  }

  getUpcomingReminders(gift: Gift): Array<{ type: string; date: string; daysUntil: number }> {
    const reminders = [];
    const now = new Date();
    
    for (const [type, dateStr] of Object.entries(gift.reminder_dates)) {
      const reminderDate = new Date(dateStr);
      const diffTime = reminderDate.getTime() - now.getTime();
      const daysUntil = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (daysUntil >= 0) {
        reminders.push({
          type,
          date: dateStr,
          daysUntil
        });
      }
    }
    
    return reminders.sort((a, b) => a.daysUntil - b.daysUntil);
  }

  generateGiftSuggestions(contactId?: number, occasion?: string, budget?: number): Promise<GiftIdea[]> {
    const params = new URLSearchParams();
    if (contactId) params.append('contact_id', contactId.toString());
    if (occasion) params.append('occasion', occasion);
    if (budget) params.append('budget', budget.toString());
    
    return this.getGiftIdeas(0, 10, {
      target_contact_id: contactId ? [contactId] : undefined,
      max_price: budget,
    });
  }
}

export const giftsService = new GiftsService();
export default giftsService;