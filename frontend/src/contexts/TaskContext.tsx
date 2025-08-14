'use client';

import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import {
  Task,
  TaskCategory,
  TaskFilters,
  TaskSortBy,
  TaskViewMode,
  CreateTaskInput,
  CreateCategoryInput,
  TaskUpdate,
  TaskCategoryUpdate,
} from '../types/Task';
import { tasksService } from '../services/tasks';

// Context types
interface TaskContextType {
  // Task state
  tasks: Task[];
  currentTask: Task | null;
  loading: boolean;
  error: string | null;
  
  // Categories state
  categories: TaskCategory[];
  categoriesLoading: boolean;
  
  // Filters and UI state
  filters: TaskFilters;
  viewMode: TaskViewMode;
  sortBy: TaskSortBy;
  
  // Actions
  createTask: (task: CreateTaskInput) => Promise<Task>;
  updateTask: (id: number, updates: Partial<Task>) => Promise<Task>;
  deleteTask: (id: number) => Promise<void>;
  toggleTaskComplete: (id: number) => Promise<void>;
  
  // Category actions
  createCategory: (category: CreateCategoryInput) => Promise<TaskCategory>;
  updateCategory: (id: number, updates: Partial<TaskCategory>) => Promise<TaskCategory>;
  deleteCategory: (id: number) => Promise<void>;
  
  // Filter actions
  setFilters: (filters: Partial<TaskFilters>) => void;
  clearFilters: () => void;
  setViewMode: (mode: TaskViewMode) => void;
  setSortBy: (sort: TaskSortBy) => void;
  
  // Data fetching
  fetchTasks: (filters?: TaskFilters) => Promise<void>;
  fetchTask: (id: number) => Promise<Task>;
  fetchCategories: () => Promise<void>;
  refreshData: () => Promise<void>;
}

// Action types
type TaskAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_TASKS'; payload: Task[] }
  | { type: 'ADD_TASK'; payload: Task }
  | { type: 'UPDATE_TASK'; payload: { id: number; task: Task } }
  | { type: 'REMOVE_TASK'; payload: number }
  | { type: 'SET_CURRENT_TASK'; payload: Task | null }
  | { type: 'SET_CATEGORIES'; payload: TaskCategory[] }
  | { type: 'SET_CATEGORIES_LOADING'; payload: boolean }
  | { type: 'ADD_CATEGORY'; payload: TaskCategory }
  | { type: 'UPDATE_CATEGORY'; payload: { id: number; category: TaskCategory } }
  | { type: 'REMOVE_CATEGORY'; payload: number }
  | { type: 'SET_FILTERS'; payload: Partial<TaskFilters> }
  | { type: 'CLEAR_FILTERS' }
  | { type: 'SET_VIEW_MODE'; payload: TaskViewMode }
  | { type: 'SET_SORT_BY'; payload: TaskSortBy }
  | { type: 'OPTIMISTIC_UPDATE_TASK'; payload: { id: number; changes: Partial<Task> } }
  | { type: 'REVERT_TASK'; payload: { id: number; originalTask: Task } };

// Initial state
const initialState = {
  tasks: [],
  currentTask: null,
  loading: false,
  error: null,
  categories: [],
  categoriesLoading: false,
  filters: {},
  viewMode: 'list' as TaskViewMode,
  sortBy: { field: 'created_at' as const, direction: 'desc' as const },
};

// Reducer
function taskReducer(state: typeof initialState, action: TaskAction): typeof initialState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    
    case 'SET_TASKS':
      return { ...state, tasks: action.payload };
    
    case 'ADD_TASK':
      return { ...state, tasks: [...state.tasks, action.payload] };
    
    case 'UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id ? action.payload.task : task
        ),
        currentTask: state.currentTask?.id === action.payload.id 
          ? action.payload.task 
          : state.currentTask,
      };
    
    case 'REMOVE_TASK':
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload),
        currentTask: state.currentTask?.id === action.payload ? null : state.currentTask,
      };
    
    case 'SET_CURRENT_TASK':
      return { ...state, currentTask: action.payload };
    
    case 'SET_CATEGORIES':
      return { ...state, categories: action.payload };
    
    case 'SET_CATEGORIES_LOADING':
      return { ...state, categoriesLoading: action.payload };
    
    case 'ADD_CATEGORY':
      return { ...state, categories: [...state.categories, action.payload] };
    
    case 'UPDATE_CATEGORY':
      return {
        ...state,
        categories: state.categories.map(cat =>
          cat.id === action.payload.id ? action.payload.category : cat
        ),
      };
    
    case 'REMOVE_CATEGORY':
      return {
        ...state,
        categories: state.categories.filter(cat => cat.id !== action.payload),
      };
    
    case 'SET_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.payload } };
    
    case 'CLEAR_FILTERS':
      return { ...state, filters: {} };
    
    case 'SET_VIEW_MODE':
      return { ...state, viewMode: action.payload };
    
    case 'SET_SORT_BY':
      return { ...state, sortBy: action.payload };
    
    case 'OPTIMISTIC_UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id 
            ? { ...task, ...action.payload.changes }
            : task
        ),
      };
    
    case 'REVERT_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id ? action.payload.originalTask : task
        ),
      };
    
    default:
      return state;
  }
}

// Create context
const TaskContext = createContext<TaskContextType | undefined>(undefined);

// Provider component
export const TaskProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(taskReducer, initialState);

  // Fetch tasks
  const fetchTasks = useCallback(async (filters?: TaskFilters) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });
      
      const actualFilters = filters || state.filters;
      const tasks = await tasksService.getTasks(0, 100, actualFilters);
      dispatch({ type: 'SET_TASKS', payload: tasks });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch tasks';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [state.filters]);

  // Fetch single task
  const fetchTask = useCallback(async (id: number): Promise<Task> => {
    try {
      const task = await tasksService.getTask(id);
      dispatch({ type: 'SET_CURRENT_TASK', payload: task });
      return task;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch task';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      dispatch({ type: 'SET_CATEGORIES_LOADING', payload: true });
      const categories = await tasksService.getCategories();
      dispatch({ type: 'SET_CATEGORIES', payload: categories });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch categories';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
    } finally {
      dispatch({ type: 'SET_CATEGORIES_LOADING', payload: false });
    }
  }, []);

  // Create task
  const createTask = useCallback(async (taskData: CreateTaskInput): Promise<Task> => {
    try {
      dispatch({ type: 'SET_ERROR', payload: null });
      const newTask = await tasksService.createTask(taskData);
      dispatch({ type: 'ADD_TASK', payload: newTask });
      return newTask;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create task';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Update task
  const updateTask = useCallback(async (id: number, updates: Partial<Task>): Promise<Task> => {
    try {
      dispatch({ type: 'SET_ERROR', payload: null });
      const updatedTask = await tasksService.updateTask(id, updates);
      dispatch({ type: 'UPDATE_TASK', payload: { id, task: updatedTask } });
      return updatedTask;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Delete task
  const deleteTask = useCallback(async (id: number): Promise<void> => {
    try {
      dispatch({ type: 'SET_ERROR', payload: null });
      await tasksService.deleteTask(id);
      dispatch({ type: 'REMOVE_TASK', payload: id });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete task';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Toggle task completion
  const toggleTaskComplete = useCallback(async (id: number): Promise<void> => {
    const task = state.tasks.find(t => t.id === id);
    if (!task) return;

    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    
    try {
      dispatch({ type: 'SET_ERROR', payload: null });
      const updatedTask = await tasksService.updateTaskStatus(id, newStatus);
      dispatch({ type: 'UPDATE_TASK', payload: { id, task: updatedTask } });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to toggle task completion';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, [state.tasks]);

  // Create category
  const createCategory = useCallback(async (categoryData: CreateCategoryInput): Promise<TaskCategory> => {
    try {
      dispatch({ type: 'SET_ERROR', payload: null });
      const newCategory = await tasksService.createTaskCategory(categoryData);
      dispatch({ type: 'ADD_CATEGORY', payload: newCategory });
      return newCategory;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create category';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Update category
  const updateCategory = useCallback(async (id: number, updates: Partial<TaskCategory>): Promise<TaskCategory> => {
    try {
      dispatch({ type: 'SET_ERROR', payload: null });
      const updatedCategory = await tasksService.updateTaskCategory(id, updates);
      dispatch({ type: 'UPDATE_CATEGORY', payload: { id, category: updatedCategory } });
      return updatedCategory;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update category';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Delete category
  const deleteCategory = useCallback(async (id: number): Promise<void> => {
    try {
      dispatch({ type: 'SET_ERROR', payload: null });
      await tasksService.deleteTaskCategory(id);
      dispatch({ type: 'REMOVE_CATEGORY', payload: id });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete category';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Filter actions
  const setFilters = useCallback((filters: Partial<TaskFilters>) => {
    dispatch({ type: 'SET_FILTERS', payload: filters });
  }, []);

  const clearFilters = useCallback(() => {
    dispatch({ type: 'CLEAR_FILTERS' });
  }, []);

  const setViewMode = useCallback((mode: TaskViewMode) => {
    dispatch({ type: 'SET_VIEW_MODE', payload: mode });
  }, []);

  const setSortBy = useCallback((sort: TaskSortBy) => {
    dispatch({ type: 'SET_SORT_BY', payload: sort });
  }, []);

  // Refresh all data
  const refreshData = useCallback(async () => {
    await Promise.all([fetchTasks(), fetchCategories()]);
  }, [fetchTasks, fetchCategories]);

  // Load initial data
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const contextValue: TaskContextType = {
    // State
    tasks: state.tasks,
    currentTask: state.currentTask,
    loading: state.loading,
    error: state.error,
    categories: state.categories,
    categoriesLoading: state.categoriesLoading,
    filters: state.filters,
    viewMode: state.viewMode,
    sortBy: state.sortBy,
    
    // Actions
    createTask,
    updateTask,
    deleteTask,
    toggleTaskComplete,
    createCategory,
    updateCategory,
    deleteCategory,
    setFilters,
    clearFilters,
    setViewMode,
    setSortBy,
    fetchTasks,
    fetchTask,
    fetchCategories,
    refreshData,
  };

  return (
    <TaskContext.Provider value={contextValue}>
      {children}
    </TaskContext.Provider>
  );
};

// Hook to use context
export const useTaskContext = () => {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTaskContext must be used within a TaskProvider');
  }
  return context;
};