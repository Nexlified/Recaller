import { renderHook, act } from '@testing-library/react';
import { useTasks, useTaskSelectors } from '../useTasks';
import { TaskProvider } from '../../contexts/TaskContext';
import { mockTasks, mockTask, mockCreateTaskData, mockOverdueTask, mockCompletedTask } from '../../__mocks__/taskMocks';
import tasksService from '../../services/tasks';

// Mock the tasks service
jest.mock('../../services/tasks', () => ({
  getTasks: jest.fn(),
  getTask: jest.fn(),
  createTask: jest.fn(),
  updateTask: jest.fn(),
  deleteTask: jest.fn(),
  toggleTaskComplete: jest.fn(),
}));

const mockTasksService = tasksService as jest.Mocked<typeof tasksService>;

// Wrapper component for the TaskProvider
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <TaskProvider>{children}</TaskProvider>
);

describe('useTasks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('throws error when used outside TaskProvider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    expect(() => {
      renderHook(() => useTasks());
    }).toThrow('useTasks must be used within TaskProvider');
    
    consoleSpy.mockRestore();
  });

  it('provides access to task context', () => {
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    expect(result.current).toHaveProperty('tasks');
    expect(result.current).toHaveProperty('loading');
    expect(result.current).toHaveProperty('error');
    expect(result.current).toHaveProperty('createTask');
    expect(result.current).toHaveProperty('updateTask');
    expect(result.current).toHaveProperty('deleteTask');
    expect(result.current).toHaveProperty('fetchTasks');
  });

  it('fetches tasks on mount', async () => {
    mockTasksService.getTasks.mockResolvedValue(mockTasks);
    
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    await act(async () => {
      await result.current.fetchTasks();
    });
    
    expect(mockTasksService.getTasks).toHaveBeenCalledWith(0, 100, result.current.filters);
    expect(result.current.tasks).toEqual(mockTasks);
    expect(result.current.loading).toBe(false);
  });

  it('creates new task successfully', async () => {
    const newTask = { ...mockTask, id: 100 };
    mockTasksService.createTask.mockResolvedValue(newTask);
    
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    await act(async () => {
      await result.current.createTask(mockCreateTaskData);
    });
    
    expect(mockTasksService.createTask).toHaveBeenCalledWith(mockCreateTaskData);
    expect(result.current.tasks).toContainEqual(newTask);
  });

  it('updates existing task', async () => {
    const updatedTask = { ...mockTask, title: 'Updated Task' };
    mockTasksService.updateTask.mockResolvedValue(updatedTask);
    
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    // First set up some initial tasks
    await act(async () => {
      // Simulate having the original task in the state
      result.current.tasks.push(mockTask);
    });
    
    await act(async () => {
      await result.current.updateTask(mockTask.id, { title: 'Updated Task' });
    });
    
    expect(mockTasksService.updateTask).toHaveBeenCalledWith(mockTask.id, { title: 'Updated Task' });
    expect(result.current.tasks).toContainEqual(expect.objectContaining({ title: 'Updated Task' }));
  });

  it('deletes task successfully', async () => {
    mockTasksService.deleteTask.mockResolvedValue();
    
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    // First add a task to delete
    await act(async () => {
      result.current.tasks.push(mockTask);
    });
    
    await act(async () => {
      await result.current.deleteTask(mockTask.id);
    });
    
    expect(mockTasksService.deleteTask).toHaveBeenCalledWith(mockTask.id);
    expect(result.current.tasks).not.toContainEqual(expect.objectContaining({ id: mockTask.id }));
  });

  it('toggles task completion status', async () => {
    const completedTask = { ...mockTask, status: 'completed' as const };
    mockTasksService.toggleTaskComplete.mockResolvedValue(completedTask);
    
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    await act(async () => {
      await result.current.toggleTaskComplete(mockTask.id);
    });
    
    expect(mockTasksService.toggleTaskComplete).toHaveBeenCalledWith(mockTask.id);
  });

  it('handles API errors gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    mockTasksService.createTask.mockRejectedValue(new Error('API Error'));
    
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    await act(async () => {
      try {
        await result.current.createTask(mockCreateTaskData);
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
      }
    });
    
    expect(result.current.error).toBe('Failed to create task');
    consoleSpy.mockRestore();
  });

  it('sets loading state during operations', async () => {
    let resolvePromise: (value: any) => void;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    mockTasksService.getTasks.mockReturnValue(promise);
    
    const { result } = renderHook(() => useTasks(), { wrapper });
    
    act(() => {
      result.current.fetchTasks();
    });
    
    expect(result.current.loading).toBe(true);
    
    await act(async () => {
      resolvePromise!(mockTasks);
      await promise;
    });
    
    expect(result.current.loading).toBe(false);
  });
});

describe('useTaskSelectors', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('provides derived task states', () => {
    const { result } = renderHook(() => useTaskSelectors(), { wrapper });
    
    expect(result.current).toHaveProperty('pendingTasks');
    expect(result.current).toHaveProperty('completedTasks');
    expect(result.current).toHaveProperty('inProgressTasks');
    expect(result.current).toHaveProperty('overdueTasks');
    expect(result.current).toHaveProperty('upcomingTasks');
    expect(result.current).toHaveProperty('todayTasks');
    expect(result.current).toHaveProperty('filteredTasks');
  });

  it('correctly filters pending tasks', () => {
    const { result } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    // Mock some tasks in the context
    act(() => {
      result.current.tasks.tasks = [
        mockTask, // pending
        mockCompletedTask, // completed
        { ...mockTask, id: 3, status: 'in_progress' as const }, // in_progress
      ];
    });
    
    expect(result.current.selectors.pendingTasks).toHaveLength(1);
    expect(result.current.selectors.pendingTasks[0].status).toBe('pending');
  });

  it('correctly filters completed tasks', () => {
    const { result } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    act(() => {
      result.current.tasks.tasks = [
        mockTask, // pending
        mockCompletedTask, // completed
        { ...mockCompletedTask, id: 3 }, // another completed
      ];
    });
    
    expect(result.current.selectors.completedTasks).toHaveLength(2);
    expect(result.current.selectors.completedTasks.every(task => task.status === 'completed')).toBe(true);
  });

  it('correctly filters in-progress tasks', () => {
    const { result } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    act(() => {
      result.current.tasks.tasks = [
        mockTask, // pending
        { ...mockTask, id: 2, status: 'in_progress' as const },
        { ...mockTask, id: 3, status: 'in_progress' as const },
      ];
    });
    
    expect(result.current.selectors.inProgressTasks).toHaveLength(2);
    expect(result.current.selectors.inProgressTasks.every(task => task.status === 'in_progress')).toBe(true);
  });

  it('correctly identifies overdue tasks', () => {
    const { result } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    // Create overdue task with past due date
    const overdueTask = {
      ...mockTask,
      id: 2,
      due_date: '2020-01-01T23:59:59Z', // Past date
      status: 'pending' as const,
    };
    
    act(() => {
      result.current.tasks.tasks = [
        mockTask, // not overdue
        overdueTask, // overdue
        mockCompletedTask, // completed, not overdue
      ];
    });
    
    expect(result.current.selectors.overdueTasks).toHaveLength(1);
    expect(result.current.selectors.overdueTasks[0].id).toBe(2);
  });

  it('correctly identifies upcoming tasks', () => {
    const { result } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    // Create upcoming task (due within a week)
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 3);
    
    const upcomingTask = {
      ...mockTask,
      id: 2,
      due_date: nextWeek.toISOString(),
      status: 'pending' as const,
    };
    
    act(() => {
      result.current.tasks.tasks = [
        mockTask, // far future due date
        upcomingTask, // upcoming
        mockCompletedTask, // completed
      ];
    });
    
    expect(result.current.selectors.upcomingTasks).toHaveLength(1);
    expect(result.current.selectors.upcomingTasks[0].id).toBe(2);
  });

  it('correctly identifies today tasks', () => {
    const { result } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    // Create task due today
    const today = new Date();
    today.setHours(23, 59, 59, 999);
    
    const todayTask = {
      ...mockTask,
      id: 2,
      due_date: today.toISOString(),
      status: 'pending' as const,
    };
    
    act(() => {
      result.current.tasks.tasks = [
        mockTask, // future due date
        todayTask, // due today
        mockCompletedTask, // completed
      ];
    });
    
    expect(result.current.selectors.todayTasks).toHaveLength(1);
    expect(result.current.selectors.todayTasks[0].id).toBe(2);
  });

  it('applies filters correctly', () => {
    const { result } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    act(() => {
      result.current.tasks.tasks = mockTasks;
      // Set some filters
      result.current.tasks.setFilters({
        status: ['pending'],
        priority: ['high'],
      });
    });
    
    // The filteredTasks should only include tasks matching the filters
    expect(result.current.selectors.filteredTasks.every(
      task => task.status === 'pending' && task.priority === 'high'
    )).toBe(true);
  });

  it('memoizes selectors to prevent unnecessary re-renders', () => {
    const { result, rerender } = renderHook(() => {
      const tasks = useTasks();
      const selectors = useTaskSelectors();
      return { tasks, selectors };
    }, { wrapper });
    
    const firstRender = result.current.selectors;
    
    // Re-render without changing tasks
    rerender();
    
    const secondRender = result.current.selectors;
    
    // The selector objects should be the same (memoized)
    expect(firstRender.pendingTasks).toBe(secondRender.pendingTasks);
    expect(firstRender.completedTasks).toBe(secondRender.completedTasks);
  });
});