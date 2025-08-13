import { useState, useEffect, useCallback } from 'react';
import { tasksService } from '../services/tasks';
import {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskFilters,
  TaskCategory,
  TaskCategoryCreate,
  TaskCategoryUpdate,
  TaskAnalytics,
  ProductivityMetrics
} from '../types/Task';

/**
 * Custom React Hook for managing tasks with loading states and error handling
 */
export const useTasks = (filters?: TaskFilters) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedTasks = await tasksService.getTasks(0, 100, filters);
      setTasks(fetchedTasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const createTask = async (taskData: TaskCreate) => {
    try {
      const newTask = await tasksService.createTask(taskData);
      setTasks(prev => [...prev, newTask]);
      return newTask;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      throw err;
    }
  };

  const updateTask = async (taskId: number, updates: TaskUpdate) => {
    try {
      const updatedTask = await tasksService.updateTask(taskId, updates);
      setTasks(prev => prev.map(task => task.id === taskId ? updatedTask : task));
      return updatedTask;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
      throw err;
    }
  };

  const deleteTask = async (taskId: number) => {
    try {
      await tasksService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      throw err;
    }
  };

  const completeTask = async (taskId: number) => {
    try {
      const completedTask = await tasksService.markTaskComplete(taskId);
      setTasks(prev => prev.map(task => task.id === taskId ? completedTask : task));
      return completedTask;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete task');
      throw err;
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    tasks,
    loading,
    error,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
    refetch: fetchTasks
  };
};

/**
 * Custom React Hook for managing task categories
 */
export const useCategories = () => {
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedCategories = await tasksService.getCategories();
      setCategories(fetchedCategories);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  };

  const createCategory = async (categoryData: TaskCategoryCreate) => {
    try {
      const newCategory = await tasksService.createTaskCategory(categoryData);
      setCategories(prev => [...prev, newCategory]);
      return newCategory;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create category');
      throw err;
    }
  };

  const updateCategory = async (categoryId: number, updates: TaskCategoryUpdate) => {
    try {
      const updatedCategory = await tasksService.updateTaskCategory(categoryId, updates);
      setCategories(prev => prev.map(cat => cat.id === categoryId ? updatedCategory : cat));
      return updatedCategory;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update category');
      throw err;
    }
  };

  const deleteCategory = async (categoryId: number) => {
    try {
      await tasksService.deleteTaskCategory(categoryId);
      setCategories(prev => prev.filter(cat => cat.id !== categoryId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete category');
      throw err;
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  return {
    categories,
    loading,
    error,
    createCategory,
    updateCategory,
    deleteCategory,
    refetch: fetchCategories
  };
};

/**
 * Custom React Hook for task details with related data
 */
export const useTaskDetails = (taskId: number) => {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTaskDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedTask = await tasksService.getTask(taskId);
      setTask(fetchedTask);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch task details');
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    if (taskId) {
      fetchTaskDetails();
    }
  }, [taskId, fetchTaskDetails]);

  return {
    task,
    loading,
    error,
    refetch: fetchTaskDetails
  };
};

/**
 * Custom React Hook for task analytics
 */
export const useTaskAnalytics = () => {
  const [analytics, setAnalytics] = useState<TaskAnalytics | null>(null);
  const [productivity, setProductivity] = useState<ProductivityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const [analyticsData, productivityData] = await Promise.all([
        tasksService.getTaskAnalytics(),
        tasksService.getProductivityMetrics()
      ]);
      setAnalytics(analyticsData);
      setProductivity(productivityData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return {
    analytics,
    productivity,
    loading,
    error,
    refetch: fetchAnalytics
  };
};