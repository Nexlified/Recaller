/**
 * Example usage of the enhanced Task Management API Service
 * 
 * This file demonstrates how to use the new API methods and React hooks
 * for task management integration.
 */

import { tasksService } from '../services/tasks';
import { useTasks } from '../hooks/useTasks';
import { useTaskCategories } from '../hooks/useTaskCategories';
import {
  TaskCreate,
  TaskRecurrenceCreate,
  TaskPriority,
  TaskStatus
} from '../types/Task';

// Example 1: Basic task operations
export const exampleBasicOperations = async () => {
  try {
    // Get all tasks
    const tasks = await tasksService.getTasks();
    console.log('All tasks:', tasks);

    // Get tasks due today
    const todayTasks = await tasksService.getTasksDueToday();
    console.log('Tasks due today:', todayTasks);

    // Get upcoming tasks
    const upcomingTasks = await tasksService.getUpcomingTasks();
    console.log('Upcoming tasks:', upcomingTasks);

    // Update task priority
    if (tasks.length > 0) {
      const updatedTask = await tasksService.updateTaskPriority(
        tasks[0].id, 
        'high' as TaskPriority
      );
      console.log('Updated task priority:', updatedTask);
    }
  } catch (error) {
    console.error('Error in basic operations:', error);
  }
};

// Example 2: Working with task categories
export const exampleCategoryOperations = async () => {
  try {
    // Create a new category
    const newCategory = await tasksService.createTaskCategory({
      name: 'Work Projects',
      color: '#3B82F6',
      description: 'Tasks related to work projects'
    });
    console.log('Created category:', newCategory);

    // Get all categories
    const categories = await tasksService.getCategories();
    console.log('All categories:', categories);

    // Get tasks in a specific category
    const tasksInCategory = await tasksService.getTasksInCategory(newCategory.id);
    console.log('Tasks in category:', tasksInCategory);

  } catch (error) {
    console.error('Error in category operations:', error);
  }
};

// Example 3: Working with task recurrence
export const exampleRecurrenceOperations = async (taskId: number) => {
  try {
    // Set up weekly recurrence
    const recurrence: TaskRecurrenceCreate = {
      recurrence_type: 'weekly',
      recurrence_interval: 1,
      days_of_week: '1,3,5', // Monday, Wednesday, Friday
      lead_time_days: 1
    };

    const taskRecurrence = await tasksService.setTaskRecurrence(taskId, recurrence);
    console.log('Set task recurrence:', taskRecurrence);

    // Get task recurrence
    const existingRecurrence = await tasksService.getTaskRecurrence(taskId);
    console.log('Existing recurrence:', existingRecurrence);

    // Update recurrence
    if (existingRecurrence) {
      const updatedRecurrence = await tasksService.updateTaskRecurrence(taskId, {
        days_of_week: '1,2,3,4,5' // Monday to Friday
      });
      console.log('Updated recurrence:', updatedRecurrence);
    }

    // Get all recurring tasks
    const recurringTasks = await tasksService.getRecurringTasks();
    console.log('All recurring tasks:', recurringTasks);

  } catch (error) {
    console.error('Error in recurrence operations:', error);
  }
};

// Example 4: Analytics and reporting
export const exampleAnalyticsOperations = async () => {
  try {
    // Get task analytics
    const analytics = await tasksService.getTaskAnalytics();
    console.log('Task analytics:', analytics);

    // Get productivity metrics
    const productivity = await tasksService.getProductivityMetrics();
    console.log('Productivity metrics:', productivity);

    // Get category analytics
    const categoryAnalytics = await tasksService.getCategoryAnalytics();
    console.log('Category analytics:', categoryAnalytics);

    // Get completion report
    const completionReport = await tasksService.getCompletionReport(
      '2025-01-01T00:00:00Z',
      '2025-01-31T23:59:59Z'
    );
    console.log('Completion report:', completionReport);

  } catch (error) {
    console.error('Error in analytics operations:', error);
  }
};

// Example 5: Using React hooks in a component
export const ExampleTaskComponent = () => {
  // Use the custom hooks
  const { tasks, loading, error, createTask, toggleTaskComplete } = useTasks();
  
  const { categories } = useTaskCategories();
  // Note: useTaskAnalytics is not implemented in new system

  if (loading) return <div>Loading tasks...</div>;
  if (error) return <div>Error: {error}</div>;

  const handleCreateTask = async () => {
    const newTaskData: TaskCreate = {
      title: 'New Task from Hook',
      description: 'Created using the useTasks hook',
      priority: 'medium' as TaskPriority,
      due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 1 week from now
    };

    try {
      await createTask(newTaskData);
      console.log('Task created successfully!');
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleCompleteTask = async (taskId: number) => {
    try {
      await toggleTaskComplete(taskId);
      console.log('Task completed successfully!');
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Task Management</h1>
      
      {/* Analytics Summary - TODO: Implement with new analytics hooks */}
      {false && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Analytics Summary</h2>
          <p>Total Tasks: {/* analytics.total_tasks */}</p>
          <p>Completion Rate: {/* (analytics.completion_rate * 100).toFixed(1) */}%</p>
          <p>Overdue Tasks: {/* analytics.overdue_tasks */}</p>
        </div>
      )}

      {/* Productivity Metrics - TODO: Implement with new analytics hooks */}
      {false && (
        <div className="mb-6 p-4 bg-green-50 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Productivity</h2>
          <p>Tasks Completed Today: {/* productivity.tasks_completed_today */}</p>
          <p>Tasks Completed This Week: {/* productivity.tasks_completed_this_week */}</p>
          <p>Most Productive Day: {/* productivity.most_productive_day */}</p>
        </div>
      )}

      {/* Task List */}
      <div className="mb-4">
        <button
          onClick={handleCreateTask}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Create New Task
        </button>
      </div>

      <div className="space-y-2">
        {tasks.map(task => (
          <div key={task.id} className="p-4 border rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold">{task.title}</h3>
                <p className="text-gray-600">{task.description}</p>
                <div className="flex gap-2 mt-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    task.priority === 'high' ? 'bg-red-100 text-red-800' :
                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {task.priority}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    task.status === 'completed' ? 'bg-green-100 text-green-800' :
                    task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {task.status}
                  </span>
                </div>
              </div>
              <div>
                {task.status !== 'completed' && (
                  <button
                    onClick={() => handleCompleteTask(task.id)}
                    className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                  >
                    Complete
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Categories */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold mb-2">Categories</h2>
        <div className="flex flex-wrap gap-2">
          {categories.map(category => (
            <span
              key={category.id}
              className="px-3 py-1 rounded-full text-sm"
              style={{ 
                backgroundColor: category.color + '20',
                color: category.color 
              }}
            >
              {category.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

// Example 6: Error handling patterns
export const exampleErrorHandling = async () => {
  try {
    // This will demonstrate proper error handling
    const task = await tasksService.getTask(999999); // Non-existent task
    console.log('Task:', task);
  } catch (error) {
    if (error instanceof Error && 'response' in error) {
      // Type assertion to handle axios error structure
      const axiosError = error as Error & {
        response?: {
          status?: number;
          data?: unknown;
        };
      };
      
      switch (axiosError.response?.status) {
        case 404:
          console.error('Task not found');
          break;
        case 401:
          console.error('Authentication required');
          // Token should be automatically cleared by interceptor
          break;
        case 403:
          console.error('Access denied for this tenant');
          break;
        case 422:
          console.error('Validation error:', axiosError.response.data);
          break;
        case 500:
          console.error('Server error occurred');
          break;
        default:
          console.error('Unexpected error:', error);
      }
    } else {
      console.error('Network or other error:', error);
    }
  }
};