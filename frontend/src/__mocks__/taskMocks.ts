import { Task, TaskCategory, TaskStatus, TaskPriority, TaskRecurrence } from '../types/Task';
import { Contact } from '../services/contacts';

// Mock Contact data
export const mockContact: Contact = {
  id: 1,
  tenant_id: 1,
  created_by_user_id: 1,
  first_name: 'John',
  last_name: 'Doe',
  email: 'john.doe@example.com',
  phone: '+1-555-0123',
  visibility: 'private',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockContacts: Contact[] = [
  mockContact,
  {
    ...mockContact,
    id: 2,
    first_name: 'Jane',
    last_name: 'Smith',
    email: 'jane.smith@example.com',
    phone: '+1-555-0124',
  },
];

// Mock Task Categories
export const mockCategory: TaskCategory = {
  id: 1,
  tenant_id: 1,
  user_id: 1,
  name: 'Work',
  color: '#FF5722',
  description: 'Work related tasks',
  created_at: '2024-01-01T00:00:00Z',
};

export const mockCategories: TaskCategory[] = [
  mockCategory,
  {
    ...mockCategory,
    id: 2,
    name: 'Personal',
    color: '#4CAF50',
    description: 'Personal tasks and reminders',
  },
  {
    ...mockCategory,
    id: 3,
    name: 'Shopping',
    color: '#2196F3',
    description: 'Shopping lists and errands',
  },
];

// Mock Task Recurrence
export const mockRecurrence: TaskRecurrence = {
  id: 1,
  task_id: 1,
  recurrence_type: 'weekly',
  recurrence_interval: 1,
  days_of_week: '1,3,5', // Mon, Wed, Fri
  day_of_month: undefined,
  end_date: undefined,
  max_occurrences: undefined,
  lead_time_days: 0,
  created_at: '2024-01-01T00:00:00Z',
};

// Mock Tasks
export const mockTask: Task = {
  id: 1,
  tenant_id: 1,
  user_id: 1,
  title: 'Test Task',
  description: 'This is a test task',
  status: 'pending' as TaskStatus,
  priority: 'medium' as TaskPriority,
  start_date: '2024-01-01T09:00:00Z',
  due_date: '2024-12-31T23:59:59Z',
  completed_at: undefined,
  is_recurring: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  categories: [mockCategory],
  contacts: [mockContact],
  recurrence: undefined,
};

export const mockRecurringTask: Task = {
  ...mockTask,
  id: 2,
  title: 'Weekly Meeting',
  description: 'Team standup meeting',
  is_recurring: true,
  recurrence: mockRecurrence,
};

export const mockCompletedTask: Task = {
  ...mockTask,
  id: 3,
  title: 'Completed Task',
  description: 'This task is already completed',
  status: 'completed' as TaskStatus,
  completed_at: '2024-01-02T14:30:00Z',
};

export const mockOverdueTask: Task = {
  ...mockTask,
  id: 4,
  title: 'Overdue Task',
  description: 'This task is overdue',
  due_date: '2024-01-01T23:59:59Z', // Past date
  priority: 'high' as TaskPriority,
};

export const mockTasks: Task[] = [
  mockTask,
  mockRecurringTask,
  mockCompletedTask,
  mockOverdueTask,
  {
    ...mockTask,
    id: 5,
    title: 'High Priority Task',
    priority: 'high' as TaskPriority,
    categories: [mockCategories[0]],
    contacts: [],
  },
  {
    ...mockTask,
    id: 6,
    title: 'In Progress Task',
    status: 'in_progress' as TaskStatus,
    categories: [mockCategories[1]],
  },
  {
    ...mockTask,
    id: 7,
    title: 'Low Priority Task',
    priority: 'low' as TaskPriority,
    due_date: '2024-02-15T10:00:00Z',
  },
];

// Mock Task Creation Data
export const mockCreateTaskData = {
  title: 'New Task',
  description: 'A new task to be created',
  status: 'pending' as TaskStatus,
  priority: 'medium' as TaskPriority,
  due_date: '2024-12-31T23:59:59Z',
  category_ids: [1],
  contact_ids: [1],
};

export const mockCreateCategoryData = {
  name: 'New Category',
  color: '#9C27B0',
  description: 'A new category for organizing tasks',
};

// Helper functions for creating mock data
export const createMockTask = (overrides: Partial<Task> = {}): Task => ({
  ...mockTask,
  ...overrides,
  id: overrides.id || Math.floor(Math.random() * 1000) + 100,
});

export const createMockCategory = (overrides: Partial<TaskCategory> = {}): TaskCategory => ({
  ...mockCategory,
  ...overrides,
  id: overrides.id || Math.floor(Math.random() * 1000) + 100,
});

// Task filters for testing
export const mockTaskFilters = {
  status: ['pending' as TaskStatus, 'in_progress' as TaskStatus],
  priority: ['high' as TaskPriority],
  category_ids: [1, 2],
  contact_ids: [1],
  due_date_start: '2024-01-01',
  due_date_end: '2024-12-31',
  is_recurring: false,
  is_overdue: false,
  search: 'test',
};

// Mock API responses
export const mockApiResponses = {
  getTasks: {
    data: mockTasks,
    status: 200,
  },
  getTask: {
    data: mockTask,
    status: 200,
  },
  createTask: {
    data: { ...mockTask, id: 100 },
    status: 201,
  },
  updateTask: {
    data: { ...mockTask, title: 'Updated Task' },
    status: 200,
  },
  deleteTask: {
    status: 204,
  },
  getCategories: {
    data: mockCategories,
    status: 200,
  },
  createCategory: {
    data: { ...mockCategory, id: 100 },
    status: 201,
  },
};

// Error responses for testing error handling
export const mockErrorResponses = {
  notFound: {
    response: {
      status: 404,
      data: { detail: 'Task not found' },
    },
  },
  unauthorized: {
    response: {
      status: 401,
      data: { detail: 'Not authenticated' },
    },
  },
  validationError: {
    response: {
      status: 422,
      data: {
        detail: [
          {
            loc: ['body', 'title'],
            msg: 'Field required',
            type: 'missing',
          },
        ],
      },
    },
  },
  serverError: {
    response: {
      status: 500,
      data: { detail: 'Internal server error' },
    },
  },
};