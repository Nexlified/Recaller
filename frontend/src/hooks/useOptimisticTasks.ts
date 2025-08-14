import { useCallback } from 'react';
import { useTasks } from './useTasks';
import { Task } from '../types/Task';

/**
 * Hook for optimistic updates to improve user experience
 */
export const useOptimisticTasks = () => {
  const { tasks, updateTask, deleteTask, toggleTaskComplete } = useTasks();
  
  /**
   * Generic optimistic update function
   */
  const optimisticUpdate = useCallback(async <T>(
    taskId: number,
    optimisticChanges: Partial<Task>,
    apiCall: () => Promise<T>,
    onSuccess?: (result: T) => void,
    onError?: (error: Error) => void
  ): Promise<T | null> => {
    // Find the original task
    const originalTask = tasks.find(t => t.id === taskId);
    if (!originalTask) {
      console.warn(`Task with id ${taskId} not found for optimistic update`);
      return null;
    }
    
    try {
      // Apply optimistic update immediately (this would be handled by context)
      // For now, we'll rely on the context to handle the optimistic state
      
      // Make the actual API call
      const result = await apiCall();
      
      // Call success callback if provided
      onSuccess?.(result);
      
      return result;
    } catch (error) {
      // Handle error and revert if needed
      const err = error instanceof Error ? error : new Error('Unknown error');
      
      // Call error callback if provided
      onError?.(err);
      
      console.error('Optimistic update failed:', err);
      throw err;
    }
  }, [tasks]);
  
  /**
   * Optimistic toggle task completion
   */
  const optimisticToggleComplete = useCallback(async (taskId: number): Promise<void> => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    const optimisticChanges: Partial<Task> = {
      status: newStatus,
      completed_at: newStatus === 'completed' ? new Date().toISOString() : undefined,
    };
    
    await optimisticUpdate(
      taskId,
      optimisticChanges,
      () => toggleTaskComplete(taskId),
      undefined,
      (error) => {
        console.error('Failed to toggle task completion:', error);
      }
    );
  }, [tasks, toggleTaskComplete, optimisticUpdate]);
  
  /**
   * Optimistic task deletion
   */
  const optimisticDelete = useCallback(async (taskId: number): Promise<void> => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    try {
      // Remove from UI immediately (handled by context)
      await deleteTask(taskId);
    } catch (error) {
      // The context should handle reverting the deletion
      console.error('Failed to delete task:', error);
      throw error;
    }
  }, [tasks, deleteTask]);
  
  /**
   * Optimistic priority update
   */
  const optimisticUpdatePriority = useCallback(async (
    taskId: number, 
    newPriority: Task['priority']
  ): Promise<void> => {
    const optimisticChanges: Partial<Task> = { priority: newPriority };
    
    await optimisticUpdate(
      taskId,
      optimisticChanges,
      () => updateTask(taskId, { priority: newPriority }),
      undefined,
      (error) => {
        console.error('Failed to update task priority:', error);
      }
    );
  }, [updateTask, optimisticUpdate]);
  
  /**
   * Optimistic status update
   */
  const optimisticUpdateStatus = useCallback(async (
    taskId: number, 
    newStatus: Task['status']
  ): Promise<void> => {
    const optimisticChanges: Partial<Task> = { 
      status: newStatus,
      completed_at: newStatus === 'completed' ? new Date().toISOString() : undefined,
    };
    
    await optimisticUpdate(
      taskId,
      optimisticChanges,
      () => updateTask(taskId, { status: newStatus }),
      undefined,
      (error) => {
        console.error('Failed to update task status:', error);
      }
    );
  }, [updateTask, optimisticUpdate]);
  
  /**
   * Optimistic due date update
   */
  const optimisticUpdateDueDate = useCallback(async (
    taskId: number, 
    newDueDate: string | undefined
  ): Promise<void> => {
    const optimisticChanges: Partial<Task> = { due_date: newDueDate };
    
    await optimisticUpdate(
      taskId,
      optimisticChanges,
      () => updateTask(taskId, { due_date: newDueDate }),
      undefined,
      (error) => {
        console.error('Failed to update task due date:', error);
      }
    );
  }, [updateTask, optimisticUpdate]);
  
  /**
   * Optimistic title update
   */
  const optimisticUpdateTitle = useCallback(async (
    taskId: number, 
    newTitle: string
  ): Promise<void> => {
    if (!newTitle.trim()) {
      throw new Error('Title cannot be empty');
    }
    
    const optimisticChanges: Partial<Task> = { title: newTitle };
    
    await optimisticUpdate(
      taskId,
      optimisticChanges,
      () => updateTask(taskId, { title: newTitle }),
      undefined,
      (error) => {
        console.error('Failed to update task title:', error);
      }
    );
  }, [updateTask, optimisticUpdate]);
  
  /**
   * Bulk optimistic operations
   */
  const optimisticBulkUpdate = useCallback(async (
    taskIds: number[],
    updates: Partial<Task>
  ): Promise<void> => {
    const promises = taskIds.map(taskId => 
      optimisticUpdate(
        taskId,
        updates,
        () => updateTask(taskId, updates)
      )
    );
    
    try {
      await Promise.all(promises);
    } catch (error) {
      console.error('Failed to perform bulk update:', error);
      throw error;
    }
  }, [updateTask, optimisticUpdate]);
  
  /**
   * Optimistic reordering (for drag and drop)
   */
  const optimisticReorder = useCallback(async (
    sourceIndex: number,
    destinationIndex: number,
    onReorder: (sourceIndex: number, destinationIndex: number) => Promise<void>
  ): Promise<void> => {
    // The actual reordering logic would depend on your backend implementation
    // This is a placeholder for the optimistic UI update
    
    try {
      await onReorder(sourceIndex, destinationIndex);
    } catch (error) {
      console.error('Failed to reorder tasks:', error);
      // Revert the optimistic reordering
      throw error;
    }
  }, []);
  
  return {
    optimisticUpdate,
    optimisticToggleComplete,
    optimisticDelete,
    optimisticUpdatePriority,
    optimisticUpdateStatus,
    optimisticUpdateDueDate,
    optimisticUpdateTitle,
    optimisticBulkUpdate,
    optimisticReorder,
  };
};

/**
 * Hook for optimistic task creation
 */
export const useOptimisticTaskCreation = () => {
  const { createTask } = useTasks();
  
  const optimisticCreateTask = useCallback(async (
    taskData: Parameters<typeof createTask>[0],
    tempId?: string
  ): Promise<Task> => {
    // Create a temporary task for immediate UI feedback
    const tempTask: Task = {
      id: parseInt(tempId || Math.random().toString().slice(2)),
      tenant_id: 0, // Will be set by backend
      user_id: 0, // Will be set by backend
      title: taskData.title,
      description: taskData.description,
      status: taskData.status || 'pending',
      priority: taskData.priority || 'medium',
      start_date: taskData.start_date,
      due_date: taskData.due_date,
      completed_at: undefined,
      is_recurring: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      categories: [],
      contacts: [],
      recurrence: taskData.recurrence ? {
        id: 0,
        task_id: 0,
        recurrence_type: taskData.recurrence.recurrence_type,
        recurrence_interval: taskData.recurrence.recurrence_interval || 1,
        days_of_week: taskData.recurrence.days_of_week,
        day_of_month: taskData.recurrence.day_of_month,
        end_date: taskData.recurrence.end_date,
        max_occurrences: taskData.recurrence.max_occurrences,
        lead_time_days: taskData.recurrence.lead_time_days || 0,
        created_at: new Date().toISOString(),
      } : undefined,
    };
    
    try {
      // Add temporary task to UI immediately
      // (This would be handled by the context in a real implementation)
      
      // Make the actual API call
      const newTask = await createTask(taskData);
      
      // Replace temp task with real task
      // (This would also be handled by the context)
      
      return newTask;
    } catch (error) {
      // Remove temp task from UI
      // (This would be handled by the context)
      
      console.error('Failed to create task:', error);
      throw error;
    }
  }, [createTask]);
  
  return {
    optimisticCreateTask,
  };
};