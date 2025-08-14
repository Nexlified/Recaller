import { useMemo } from 'react';
import { useTaskContext } from '../contexts/TaskContext';
import { Task, TaskFilters } from '../types/Task';

/**
 * Core hook to access task context
 */
export const useTasks = () => {
  const context = useTaskContext();
  if (!context) {
    throw new Error('useTasks must be used within TaskProvider');
  }
  return context;
};

/**
 * Hook for derived state selectors
 */
export const useTaskSelectors = () => {
  const { tasks, filters } = useTasks();
  
  const pendingTasks = useMemo(
    () => tasks.filter(task => task.status === 'pending'),
    [tasks]
  );
  
  const completedTasks = useMemo(
    () => tasks.filter(task => task.status === 'completed'),
    [tasks]
  );
  
  const inProgressTasks = useMemo(
    () => tasks.filter(task => task.status === 'in_progress'),
    [tasks]
  );
  
  const overdueTasks = useMemo(
    () => tasks.filter(task => 
      task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed'
    ),
    [tasks]
  );
  
  const upcomingTasks = useMemo(
    () => tasks.filter(task => {
      if (!task.due_date) return false;
      const dueDate = new Date(task.due_date);
      const now = new Date();
      const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
      return dueDate >= now && dueDate <= nextWeek && task.status !== 'completed';
    }),
    [tasks]
  );
  
  const todayTasks = useMemo(
    () => tasks.filter(task => {
      if (!task.due_date) return false;
      const dueDate = new Date(task.due_date);
      const today = new Date();
      return dueDate.toDateString() === today.toDateString() && task.status !== 'completed';
    }),
    [tasks]
  );
  
  const filteredTasks = useMemo(
    () => applyFilters(tasks, filters),
    [tasks, filters]
  );
  
  return {
    pendingTasks,
    completedTasks,
    inProgressTasks,
    overdueTasks,
    upcomingTasks,
    todayTasks,
    filteredTasks,
  };
};

/**
 * Apply filters to tasks array
 */
function applyFilters(tasks: Task[], filters: TaskFilters): Task[] {
  return tasks.filter(task => {
    // Status filter
    if (filters.status && filters.status.length > 0) {
      if (!filters.status.includes(task.status)) return false;
    }
    
    // Priority filter
    if (filters.priority && filters.priority.length > 0) {
      if (!filters.priority.includes(task.priority)) return false;
    }
    
    // Category filter
    if (filters.category_ids && filters.category_ids.length > 0) {
      const taskCategoryIds = task.categories.map(cat => cat.id);
      if (!filters.category_ids.some(id => taskCategoryIds.includes(id))) return false;
    }
    
    // Contact filter
    if (filters.contact_ids && filters.contact_ids.length > 0) {
      const taskContactIds = task.contacts.map(contact => contact.id);
      if (!filters.contact_ids.some(id => taskContactIds.includes(id))) return false;
    }
    
    // Date range filter
    if (filters.due_date_start && task.due_date) {
      if (new Date(task.due_date) < new Date(filters.due_date_start)) return false;
    }
    
    if (filters.due_date_end && task.due_date) {
      if (new Date(task.due_date) > new Date(filters.due_date_end)) return false;
    }
    
    // Recurring filter
    if (filters.is_recurring !== undefined) {
      if (task.is_recurring !== filters.is_recurring) return false;
    }
    
    // Overdue filter
    if (filters.is_overdue !== undefined) {
      const isOverdue = task.due_date && 
        new Date(task.due_date) < new Date() && 
        task.status !== 'completed';
      if (Boolean(isOverdue) !== filters.is_overdue) return false;
    }
    
    // Search filter
    if (filters.search && filters.search.trim()) {
      const searchTerm = filters.search.toLowerCase();
      const searchableText = [
        task.title,
        task.description || '',
        ...task.categories.map(cat => cat.name),
        ...task.contacts.map(contact => contact.first_name + ' ' + contact.last_name),
      ].join(' ').toLowerCase();
      
      if (!searchableText.includes(searchTerm)) return false;
    }
    
    return true;
  });
}