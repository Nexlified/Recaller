import api from './api';
import { AxiosError } from 'axios';
import {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskCategory,
  TaskCategoryCreate,
  TaskCategoryUpdate,
  TaskFilters,
  TaskSearchQuery,
  TaskBulkUpdate,
  TaskContactCreate,
  TaskCategoryAssignmentCreate,
  TaskStatus,
  TaskPriority,
  TaskRecurrence,
  TaskRecurrenceCreate,
  TaskRecurrenceUpdate,
  TaskAnalytics,
  ProductivityMetrics,
  CategoryAnalytics,
  CompletionReport
} from '../types/Task';
import { Contact } from './contacts';

class TasksService {
  // Task CRUD operations
  async getTasks(skip: number = 0, limit: number = 100, filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    // Add filters to query params
    if (filters) {
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.is_recurring !== undefined) params.append('is_recurring', filters.is_recurring.toString());
      if (filters.is_overdue !== undefined) params.append('is_overdue', filters.is_overdue.toString());
      if (filters.due_date_start) params.append('due_date_from', filters.due_date_start);
      if (filters.due_date_end) params.append('due_date_to', filters.due_date_end);
      if (filters.category_ids && filters.category_ids.length > 0) {
        filters.category_ids.forEach(id => params.append('category_id', id.toString()));
      }
      if (filters.contact_ids && filters.contact_ids.length > 0) {
        filters.contact_ids.forEach(id => params.append('contact_id', id.toString()));
      }
    }

    const response = await api.get<Task[]>(`/tasks/?${params.toString()}`);
    return response.data;
  }

  async getTask(taskId: number): Promise<Task> {
    const response = await api.get<Task>(`/tasks/${taskId}`);
    return response.data;
  }

  async createTask(taskData: TaskCreate): Promise<Task> {
    const response = await api.post<Task>('/tasks/', taskData);
    return response.data;
  }

  async updateTask(taskId: number, taskData: TaskUpdate): Promise<Task> {
    const response = await api.put<Task>(`/tasks/${taskId}`, taskData);
    return response.data;
  }

  async deleteTask(taskId: number): Promise<void> {
    await api.delete(`/tasks/${taskId}`);
  }

  // Task status operations
  async updateTaskStatus(taskId: number, status: TaskStatus): Promise<Task> {
    const response = await api.put<Task>(`/tasks/${taskId}/status?status=${status}`);
    return response.data;
  }

  async updateTaskPriority(taskId: number, priority: TaskPriority): Promise<Task> {
    const response = await api.put<Task>(`/tasks/${taskId}/priority?priority=${priority}`);
    return response.data;
  }

  async markTaskComplete(taskId: number): Promise<Task> {
    const response = await api.put<Task>(`/tasks/${taskId}/complete`);
    return response.data;
  }

  // Task filtering and search
  async getTasksByStatus(status: TaskStatus, skip: number = 0, limit: number = 100): Promise<Task[]> {
    const response = await api.get<Task[]>(`/tasks/status/${status}?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getOverdueTasks(skip: number = 0, limit: number = 100): Promise<Task[]> {
    const response = await api.get<Task[]>(`/tasks/overdue?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getTasksDueToday(skip: number = 0, limit: number = 100): Promise<Task[]> {
    const response = await api.get<Task[]>(`/tasks/due-today?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getUpcomingTasks(skip: number = 0, limit: number = 100): Promise<Task[]> {
    const response = await api.get<Task[]>(`/tasks/upcoming?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async searchTasks(query: TaskSearchQuery, skip: number = 0, limit: number = 100): Promise<Task[]> {
    const params = new URLSearchParams({
      q: query.query,
      skip: skip.toString(),
      limit: limit.toString(),
    });

    if (query.status) params.append('status', query.status);
    if (query.priority) params.append('priority', query.priority);
    if (query.start_date) params.append('start_date', query.start_date);
    if (query.end_date) params.append('end_date', query.end_date);
    if (query.category_ids && query.category_ids.length > 0) {
      query.category_ids.forEach(id => params.append('category_id', id.toString()));
    }
    if (query.contact_ids && query.contact_ids.length > 0) {
      query.contact_ids.forEach(id => params.append('contact_id', id.toString()));
    }

    const response = await api.get<Task[]>(`/tasks/search/?${params.toString()}`);
    return response.data;
  }

  // Bulk operations
  async bulkUpdateTasks(bulkUpdate: TaskBulkUpdate): Promise<{ updated_count: number }> {
    const response = await api.put<{ updated_count: number }>('/tasks/bulk-update', bulkUpdate);
    return response.data;
  }

  // Task-Contact associations
  async assignContactToTask(taskId: number, contactData: TaskContactCreate): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(`/tasks/${taskId}/contacts`, contactData);
    return response.data;
  }

  async removeContactFromTask(taskId: number, contactId: number): Promise<void> {
    await api.delete(`/tasks/${taskId}/contacts/${contactId}`);
  }

  async getTaskContacts(taskId: number): Promise<Contact[]> {
    const response = await api.get<Contact[]>(`/tasks/${taskId}/contacts`);
    return response.data;
  }

  async addContactToTask(taskId: number, contactId: number, context?: string): Promise<void> {
    const contactData: TaskContactCreate = {
      contact_id: contactId,
      relationship_context: context
    };
    await this.assignContactToTask(taskId, contactData);
  }

  async getTasksForContact(contactId: number): Promise<Task[]> {
    const response = await api.get<Task[]>(`/contacts/${contactId}/tasks`);
    return response.data;
  }

  // Task-Category associations
  async assignCategoryToTask(taskId: number, categoryData: TaskCategoryAssignmentCreate): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(`/tasks/${taskId}/categories`, categoryData);
    return response.data;
  }

  async removeCategoryFromTask(taskId: number, categoryId: number): Promise<void> {
    await api.delete(`/tasks/${taskId}/categories/${categoryId}`);
  }

  async getTaskCategories(taskId: number): Promise<TaskCategory[]> {
    const response = await api.get<TaskCategory[]>(`/tasks/${taskId}/categories`);
    return response.data;
  }

  async getTasksInCategory(categoryId: number): Promise<Task[]> {
    const response = await api.get<Task[]>(`/task-categories/${categoryId}/tasks`);
    return response.data;
  }

  // Task Categories CRUD
  async getCategories(skip: number = 0, limit: number = 100): Promise<TaskCategory[]> {
    const response = await api.get<TaskCategory[]>(`/task-categories/?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getTaskCategory(categoryId: number): Promise<TaskCategory> {
    const response = await api.get<TaskCategory>(`/task-categories/${categoryId}`);
    return response.data;
  }

  async createTaskCategory(categoryData: TaskCategoryCreate): Promise<TaskCategory> {
    const response = await api.post<TaskCategory>('/task-categories/', categoryData);
    return response.data;
  }

  async updateTaskCategory(categoryId: number, categoryData: TaskCategoryUpdate): Promise<TaskCategory> {
    const response = await api.put<TaskCategory>(`/task-categories/${categoryId}`, categoryData);
    return response.data;
  }

  async deleteTaskCategory(categoryId: number): Promise<void> {
    await api.delete(`/task-categories/${categoryId}`);
  }

  async searchTaskCategories(query: string, skip: number = 0, limit: number = 100): Promise<TaskCategory[]> {
    const response = await api.get<TaskCategory[]>(`/task-categories/search/?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`);
    return response.data;
  }

  // Recurrence Management
  async getTaskRecurrence(taskId: number): Promise<TaskRecurrence | null> {
    try {
      const response = await api.get<TaskRecurrence>(`/tasks/${taskId}/recurrence`);
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response?.status === 404) {
        return null; // No recurrence found
      }
      throw error;
    }
  }

  async setTaskRecurrence(taskId: number, recurrence: TaskRecurrenceCreate): Promise<TaskRecurrence> {
    const response = await api.post<TaskRecurrence>(`/tasks/${taskId}/recurrence`, recurrence);
    return response.data;
  }

  async updateTaskRecurrence(taskId: number, updates: TaskRecurrenceUpdate): Promise<TaskRecurrence> {
    const response = await api.put<TaskRecurrence>(`/tasks/${taskId}/recurrence`, updates);
    return response.data;
  }

  async removeTaskRecurrence(taskId: number): Promise<void> {
    await api.delete(`/tasks/${taskId}/recurrence`);
  }

  async getRecurringTasks(skip: number = 0, limit: number = 100): Promise<Task[]> {
    const response = await api.get<Task[]>(`/tasks/recurring?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  // Analytics & Reports
  async getTaskAnalytics(): Promise<TaskAnalytics> {
    const response = await api.get<TaskAnalytics>('/tasks/analytics/overview');
    return response.data;
  }

  async getProductivityMetrics(): Promise<ProductivityMetrics> {
    const response = await api.get<ProductivityMetrics>('/tasks/analytics/productivity');
    return response.data;
  }

  async getCategoryAnalytics(): Promise<CategoryAnalytics[]> {
    const response = await api.get<CategoryAnalytics[]>('/tasks/analytics/categories');
    return response.data;
  }

  async getCompletionReport(startDate?: string, endDate?: string): Promise<CompletionReport> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const url = `/tasks/reports/completion${params.toString() ? `?${params.toString()}` : ''}`;
    const response = await api.get<CompletionReport>(url);
    return response.data;
  }

  // Utility methods
  isTaskOverdue(task: Task): boolean {
    if (!task.due_date || task.status === 'completed' || task.status === 'cancelled') {
      return false;
    }
    return new Date(task.due_date) < new Date();
  }

  getTaskDisplayName(task: Task): string {
    return task.title.trim() || 'Untitled Task';
  }

  getTaskPriorityColor(priority: TaskPriority): string {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'yellow';
      case 'low': return 'green';
      default: return 'gray';
    }
  }

  getTaskStatusColor(status: TaskStatus): string {
    switch (status) {
      case 'completed': return 'green';
      case 'in_progress': return 'blue';
      case 'pending': return 'gray';
      case 'cancelled': return 'red';
      default: return 'gray';
    }
  }

  formatDueDate(dueDate: string): string {
    const date = new Date(dueDate);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays === -1) return 'Due yesterday';
    if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays < 7) return `Due in ${diffDays} days`;
    
    return date.toLocaleDateString();
  }
}

export const tasksService = new TasksService();
export default tasksService;