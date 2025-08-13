// Import Contact interface from the existing contacts service
import { Contact } from '../services/contacts';

// Task status and priority enums matching backend
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high';

// Recurrence types
export type RecurrenceType = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';

// Core Task interface
export interface Task {
  id: number;
  tenant_id: number;
  user_id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  start_date?: string; // ISO string
  due_date?: string; // ISO string
  completed_at?: string; // ISO string
  is_recurring: boolean;
  created_at: string; // ISO string
  updated_at?: string; // ISO string
  categories: TaskCategory[];
  contacts: Contact[];
  recurrence?: TaskRecurrence;
}

// Task creation interface
export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  start_date?: string; // ISO string
  due_date?: string; // ISO string
  category_ids?: number[];
  contact_ids?: number[];
  recurrence?: TaskRecurrenceCreate;
}

// Task update interface
export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  start_date?: string; // ISO string
  due_date?: string; // ISO string
}

// Task Category interface
export interface TaskCategory {
  id: number;
  tenant_id: number;
  user_id: number;
  name: string;
  color?: string; // Hex color code like #FF5733
  description?: string;
  created_at: string; // ISO string
}

// Task Category creation interface
export interface TaskCategoryCreate {
  name: string;
  color?: string;
  description?: string;
}

// Task Category update interface
export interface TaskCategoryUpdate {
  name?: string;
  color?: string;
  description?: string;
}

// Task Recurrence interface
export interface TaskRecurrence {
  id: number;
  task_id: number;
  recurrence_type: RecurrenceType;
  recurrence_interval: number;
  days_of_week?: string; // e.g., "1,3,5" for Mon, Wed, Fri
  day_of_month?: number; // 1-31
  end_date?: string; // ISO string
  max_occurrences?: number;
  lead_time_days: number;
  created_at: string; // ISO string
}

// Task Recurrence creation interface
export interface TaskRecurrenceCreate {
  recurrence_type: RecurrenceType;
  recurrence_interval?: number;
  days_of_week?: string;
  day_of_month?: number;
  end_date?: string; // ISO string
  max_occurrences?: number;
  lead_time_days?: number;
}

// Task Contact Association
export interface TaskContactCreate {
  contact_id: number;
  relationship_context?: string;
}

// Task Category Assignment
export interface TaskCategoryAssignmentCreate {
  category_id: number;
}

// Filtering interfaces
export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  category_ids?: number[];
  contact_ids?: number[];
  due_date_start?: string; // ISO string
  due_date_end?: string; // ISO string
  is_recurring?: boolean;
  is_overdue?: boolean;
}

// Search interface
export interface TaskSearchQuery {
  query: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  category_ids?: number[];
  contact_ids?: number[];
  start_date?: string; // ISO string
  end_date?: string; // ISO string
}

// Bulk operations
export interface TaskBulkUpdate {
  task_ids: number[];
  status?: TaskStatus;
  priority?: TaskPriority;
}

// Constants for UI
export const TASK_STATUS_OPTIONS: { value: TaskStatus; label: string; color: string }[] = [
  { value: 'pending', label: 'Pending', color: 'gray' },
  { value: 'in_progress', label: 'In Progress', color: 'blue' },
  { value: 'completed', label: 'Completed', color: 'green' },
  { value: 'cancelled', label: 'Cancelled', color: 'red' },
];

export const TASK_PRIORITY_OPTIONS: { value: TaskPriority; label: string; color: string }[] = [
  { value: 'low', label: 'Low', color: 'green' },
  { value: 'medium', label: 'Medium', color: 'yellow' },
  { value: 'high', label: 'High', color: 'red' },
];

export const RECURRENCE_TYPE_OPTIONS: { value: RecurrenceType; label: string }[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'yearly', label: 'Yearly' },
  { value: 'custom', label: 'Custom' },
];