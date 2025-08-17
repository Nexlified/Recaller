// Import Contact interface from the existing contacts service
import { Contact } from '../services/contacts';

// Gift status and priority enums matching backend
export type GiftStatus = 'idea' | 'planned' | 'purchased' | 'wrapped' | 'given' | 'returned';
export type GiftPriority = 1 | 2 | 3 | 4; // LOW, MEDIUM, HIGH, URGENT

// Core Gift interface
export interface Gift {
  id: number;
  tenant_id: number;
  user_id: number;
  title: string;
  description?: string;
  category?: string;
  recipient_contact_id?: number;
  recipient_name?: string;
  occasion?: string;
  occasion_date?: string; // ISO string
  budget_amount?: number;
  actual_amount?: number;
  currency: string;
  status: GiftStatus;
  priority: GiftPriority;
  store_name?: string;
  purchase_url?: string;
  purchase_date?: string; // ISO string
  gift_details: Record<string, any>;
  tracking_number?: string;
  delivery_date?: string; // ISO string
  notes?: string;
  image_url?: string;
  reminder_dates: Record<string, string>; // JSON with reminder types and dates
  task_id?: number;
  transaction_id?: number;
  is_active: boolean;
  is_surprise: boolean;
  created_at: string; // ISO string
  updated_at?: string; // ISO string
}

// Gift creation interface
export interface GiftCreate {
  title: string;
  description?: string;
  category?: string;
  recipient_contact_id?: number;
  recipient_name?: string;
  occasion?: string;
  occasion_date?: string; // ISO string
  budget_amount?: number;
  currency?: string;
  status?: GiftStatus;
  priority?: GiftPriority;
  store_name?: string;
  purchase_url?: string;
  purchase_date?: string; // ISO string
  gift_details?: Record<string, any>;
  tracking_number?: string;
  delivery_date?: string; // ISO string
  notes?: string;
  image_url?: string;
  reminder_dates?: Record<string, string>;
  is_surprise?: boolean;
}

// Gift update interface
export interface GiftUpdate {
  title?: string;
  description?: string;
  category?: string;
  recipient_contact_id?: number;
  recipient_name?: string;
  occasion?: string;
  occasion_date?: string; // ISO string
  budget_amount?: number;
  actual_amount?: number;
  currency?: string;
  status?: GiftStatus;
  priority?: GiftPriority;
  store_name?: string;
  purchase_url?: string;
  purchase_date?: string; // ISO string
  gift_details?: Record<string, any>;
  tracking_number?: string;
  delivery_date?: string; // ISO string
  notes?: string;
  image_url?: string;
  reminder_dates?: Record<string, string>;
  is_surprise?: boolean;
}

// Gift Idea interface
export interface GiftIdea {
  id: number;
  tenant_id: number;
  user_id: number;
  title: string;
  description?: string;
  category?: string;
  target_contact_id?: number;
  target_demographic?: string;
  suitable_occasions: string[];
  price_range_min?: number;
  price_range_max?: number;
  currency: string;
  idea_details: Record<string, any>;
  source_url?: string;
  source_description?: string;
  image_url?: string;
  rating?: number; // 1-5 star rating
  notes?: string;
  times_gifted: number;
  last_gifted_date?: string; // ISO string
  tags: string[];
  is_active: boolean;
  created_at: string; // ISO string
  updated_at?: string; // ISO string
}

// Gift Idea creation interface
export interface GiftIdeaCreate {
  title: string;
  description?: string;
  category?: string;
  target_contact_id?: number;
  target_demographic?: string;
  suitable_occasions?: string[];
  price_range_min?: number;
  price_range_max?: number;
  currency?: string;
  idea_details?: Record<string, any>;
  source_url?: string;
  source_description?: string;
  image_url?: string;
  rating?: number;
  notes?: string;
  tags?: string[];
}

// Gift Idea update interface
export interface GiftIdeaUpdate {
  title?: string;
  description?: string;
  category?: string;
  target_contact_id?: number;
  target_demographic?: string;
  suitable_occasions?: string[];
  price_range_min?: number;
  price_range_max?: number;
  currency?: string;
  idea_details?: Record<string, any>;
  source_url?: string;
  source_description?: string;
  image_url?: string;
  rating?: number;
  notes?: string;
  tags?: string[];
}

// Filtering interfaces
export interface GiftFilters {
  status?: GiftStatus[];
  category?: string[];
  occasion?: string[];
  recipient_contact_id?: number[];
  min_budget?: number;
  max_budget?: number;
  currency?: string;
  is_surprise?: boolean;
  search?: string;
}

export interface GiftIdeaFilters {
  category?: string[];
  target_contact_id?: number[];
  min_rating?: number;
  min_price?: number;
  max_price?: number;
  currency?: string;
  is_favorite?: boolean;
  search?: string;
}

// Budget tracking interfaces
export interface GiftBudget {
  total_budget: number;
  spent_amount: number;
  remaining_budget: number;
  currency: string;
  period_start?: string;
  period_end?: string;
}

export interface BudgetInsight {
  category: string;
  budgeted: number;
  spent: number;
  remaining: number;
  percentage_used: number;
}

// Analytics interfaces
export interface GiftAnalytics {
  total_gifts: number;
  total_ideas: number;
  gifts_given: number;
  total_spent: number;
  average_gift_value: number;
  top_categories: Array<{ category: string; count: number }>;
  upcoming_occasions: Array<{ occasion: string; date: string; gifts_planned: number }>;
}

// Reference data interfaces
export interface GiftCategoryReference {
  name: string;
  description: string;
  typical_price_range: string;
  occasions: string[];
  icon?: string;
}

export interface GiftOccasionReference {
  name: string;
  type: 'annual' | 'milestone' | 'spontaneous';
  importance: 'low' | 'medium' | 'high';
  advance_notice_days: number[];
  typical_budget_range: string;
  fixed_date?: string; // MM-DD format
}

export interface GiftBudgetRangeReference {
  name: string;
  min_amount: number;
  max_amount: number;
  currency: string;
  description: string;
  suggested_categories: string[];
}

// Constants for UI
export const GIFT_STATUS_OPTIONS: { value: GiftStatus; label: string; color: string }[] = [
  { value: 'idea', label: 'Idea', color: 'gray' },
  { value: 'planned', label: 'Planned', color: 'blue' },
  { value: 'purchased', label: 'Purchased', color: 'yellow' },
  { value: 'wrapped', label: 'Wrapped', color: 'purple' },
  { value: 'given', label: 'Given', color: 'green' },
  { value: 'returned', label: 'Returned', color: 'red' },
];

export const GIFT_PRIORITY_OPTIONS: { value: GiftPriority; label: string; color: string }[] = [
  { value: 1, label: 'Low', color: 'green' },
  { value: 2, label: 'Medium', color: 'yellow' },
  { value: 3, label: 'High', color: 'orange' },
  { value: 4, label: 'Urgent', color: 'red' },
];

export const GIFT_CATEGORIES = [
  'Electronics',
  'Clothing',
  'Books',
  'Jewelry',
  'Home & Garden',
  'Sports & Outdoors',
  'Food & Beverages',
  'Health & Beauty',
  'Toys & Games',
  'Art & Crafts',
  'Music & Media',
  'Travel',
  'Experience',
  'Other'
];

export const GIFT_OCCASIONS = [
  'Birthday',
  'Christmas',
  'Anniversary',
  'Valentine\'s Day',
  'Mother\'s Day',
  'Father\'s Day',
  'Graduation',
  'Wedding',
  'Housewarming',
  'Baby Shower',
  'Retirement',
  'Promotion',
  'Just Because',
  'Thank You',
  'Apology',
  'Other'
];

// Gift form data interface
export interface GiftFormData {
  title: string;
  description: string;
  category: string;
  recipient_contact_id: number | null;
  recipient_name: string;
  occasion: string;
  occasion_date: string;
  budget_amount: string;
  currency: string;
  status: GiftStatus;
  priority: GiftPriority;
  store_name: string;
  purchase_url: string;
  gift_details: Record<string, any>;
  notes: string;
  is_surprise: boolean;
}

export interface GiftIdeaFormData {
  title: string;
  description: string;
  category: string;
  target_contact_id: number | null;
  target_demographic: string;
  suitable_occasions: string[];
  price_range_min: string;
  price_range_max: string;
  currency: string;
  source_url: string;
  rating: number;
  notes: string;
  tags: string[];
}

// Validation interfaces
export interface ValidationErrors {
  [key: string]: string;
}

// Sort interfaces
export interface GiftSortBy {
  field: 'title' | 'occasion_date' | 'budget_amount' | 'created_at' | 'status' | 'priority';
  direction: 'asc' | 'desc';
}

export interface GiftIdeaSortBy {
  field: 'title' | 'rating' | 'price_range_min' | 'created_at' | 'times_gifted';
  direction: 'asc' | 'desc';
}

// View mode for gift display
export type GiftViewMode = 'list' | 'grid' | 'timeline';