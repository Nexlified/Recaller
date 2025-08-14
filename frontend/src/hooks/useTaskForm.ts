import { useState, useMemo } from 'react';
import { useTasks } from './useTasks';
import { 
  Task, 
  TaskFormData, 
  ValidationErrors, 
  CreateTaskInput,
  TaskUpdate 
} from '../types/Task';

/**
 * Hook for managing task form state and validation
 */
export const useTaskForm = (initialTask?: Task) => {
  const { createTask, updateTask } = useTasks();
  
  const [formData, setFormData] = useState<TaskFormData>(
    initialTask ? taskToFormData(initialTask) : getDefaultFormData()
  );
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const updateField = (field: keyof TaskFormData, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { [field]: _, ...rest } = prev;
        return rest;
      });
    }
  };
  
  const validateForm = (): boolean => {
    const errors = validateTaskFormData(formData);
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const submitForm = async (): Promise<Task | null> => {
    if (!validateForm()) return null;
    
    setIsSubmitting(true);
    try {
      const task = initialTask 
        ? await updateTask(initialTask.id, formDataToTaskUpdate(formData))
        : await createTask(formDataToCreateInput(formData));
      
      return task;
    } catch (error) {
      console.error('Form submission error:', error);
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const resetForm = () => {
    setFormData(getDefaultFormData());
    setValidationErrors({});
  };
  
  const isValid = useMemo(
    () => Object.keys(validationErrors).length === 0,
    [validationErrors]
  );
  
  return {
    formData,
    validationErrors,
    isSubmitting,
    updateField,
    submitForm,
    resetForm,
    isValid,
  };
};

/**
 * Get default form data
 */
function getDefaultFormData(): TaskFormData {
  return {
    title: '',
    description: '',
    status: 'pending',
    priority: 'medium',
    start_date: '',
    due_date: '',
    category_ids: [],
    contact_ids: [],
  };
}

/**
 * Convert task to form data
 */
function taskToFormData(task: Task): TaskFormData {
  return {
    title: task.title,
    description: task.description || '',
    status: task.status,
    priority: task.priority,
    start_date: task.start_date || '',
    due_date: task.due_date || '',
    category_ids: task.categories.map(cat => cat.id),
    contact_ids: task.contacts.map(contact => contact.id),
    recurrence: task.recurrence ? {
      recurrence_type: task.recurrence.recurrence_type,
      recurrence_interval: task.recurrence.recurrence_interval,
      days_of_week: task.recurrence.days_of_week,
      day_of_month: task.recurrence.day_of_month,
      end_date: task.recurrence.end_date,
      max_occurrences: task.recurrence.max_occurrences,
      lead_time_days: task.recurrence.lead_time_days,
    } : undefined,
  };
}

/**
 * Convert form data to create input
 */
function formDataToCreateInput(formData: TaskFormData): CreateTaskInput {
  const input: CreateTaskInput = {
    title: formData.title,
    description: formData.description || undefined,
    status: formData.status,
    priority: formData.priority,
    start_date: formData.start_date || undefined,
    due_date: formData.due_date || undefined,
    category_ids: formData.category_ids.length > 0 ? formData.category_ids : undefined,
    contact_ids: formData.contact_ids.length > 0 ? formData.contact_ids : undefined,
    recurrence: formData.recurrence,
  };
  
  return input;
}

/**
 * Convert form data to task update
 */
function formDataToTaskUpdate(formData: TaskFormData): TaskUpdate {
  const update: TaskUpdate = {
    title: formData.title,
    description: formData.description || undefined,
    status: formData.status,
    priority: formData.priority,
    start_date: formData.start_date || undefined,
    due_date: formData.due_date || undefined,
  };
  
  return update;
}

/**
 * Validate task form data
 */
function validateTaskFormData(formData: TaskFormData): ValidationErrors {
  const errors: ValidationErrors = {};
  
  // Title is required
  if (!formData.title.trim()) {
    errors.title = 'Title is required';
  } else if (formData.title.length > 200) {
    errors.title = 'Title must be less than 200 characters';
  }
  
  // Description length check
  if (formData.description && formData.description.length > 1000) {
    errors.description = 'Description must be less than 1000 characters';
  }
  
  // Date validation
  if (formData.start_date && formData.due_date) {
    const startDate = new Date(formData.start_date);
    const dueDate = new Date(formData.due_date);
    
    if (dueDate < startDate) {
      errors.due_date = 'Due date must be after start date';
    }
  }
  
  // Recurrence validation
  if (formData.recurrence) {
    const { recurrence_type, recurrence_interval, end_date, max_occurrences } = formData.recurrence;
    
    if (recurrence_interval && recurrence_interval < 1) {
      errors.recurrence = 'Recurrence interval must be at least 1';
    }
    
    if (end_date && formData.due_date && new Date(end_date) < new Date(formData.due_date)) {
      errors.recurrence = 'Recurrence end date must be after due date';
    }
    
    if (max_occurrences && max_occurrences < 1) {
      errors.recurrence = 'Maximum occurrences must be at least 1';
    }
    
    // Custom validation for different recurrence types
    if (recurrence_type === 'weekly' && !formData.recurrence.days_of_week) {
      errors.recurrence = 'Days of week are required for weekly recurrence';
    }
    
    if (recurrence_type === 'monthly' && !formData.recurrence.day_of_month) {
      errors.recurrence = 'Day of month is required for monthly recurrence';
    }
  }
  
  return errors;
}