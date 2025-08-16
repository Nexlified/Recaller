import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TaskItem } from '../TaskItem';
import { Task } from '../../../types/Task';
import tasksService from '../../../services/tasks';

// Mock the services
jest.mock('../../../services/tasks');
const mockTasksService = tasksService as jest.Mocked<typeof tasksService>;

// Mock the badge components
jest.mock('../TaskStatusBadge', () => ({
  TaskStatusBadge: ({ status }: { status: string }) => <span data-testid="status-badge">{status}</span>,
}));

jest.mock('../TaskPriorityBadge', () => ({
  TaskPriorityBadge: ({ priority }: { priority: string }) => <span data-testid="priority-badge">{priority}</span>,
}));

jest.mock('../DueDateIndicator', () => ({
  DueDateIndicator: ({ dueDate }: { dueDate?: string }) => <span data-testid="due-date">{dueDate}</span>,
}));

const mockTask: Task = {
  id: 1,
  tenant_id: 1,
  user_id: 1,
  title: 'Test Task',
  description: 'Test Description',
  status: 'pending',
  priority: 'medium',
  start_date: '2024-01-01T10:00:00Z',
  due_date: '2024-01-02T10:00:00Z',
  is_recurring: false,
  created_at: '2024-01-01T00:00:00Z',
  categories: [],
  contacts: [],
};

describe('TaskItem', () => {
  const mockOnUpdate = jest.fn();
  const mockOnDelete = jest.fn();
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock confirm dialog
    window.confirm = jest.fn(() => true);
    
    // Setup service mocks
    mockTasksService.deleteTask.mockResolvedValue();
    mockTasksService.updateTaskStatus.mockResolvedValue({
      ...mockTask,
      status: 'completed',
    });
    mockTasksService.isTaskOverdue.mockReturnValue(false);
  });

  test('renders task information correctly', () => {
    render(
      <TaskItem
        task={mockTask}
        onUpdate={mockOnUpdate}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  test('calls delete handler when delete button is clicked', async () => {
    render(
      <TaskItem
        task={mockTask}
        onUpdate={mockOnUpdate}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    // Find the delete button - it should be visible on hover or in actions
    const taskElement = screen.getByText('Test Task').closest('div');
    fireEvent.mouseEnter(taskElement!);

    // Look for delete button by icon or aria-label
    const deleteButton = screen.getByLabelText(/delete/i) || screen.getByTitle(/delete/i);
    expect(deleteButton).toBeInTheDocument();

    fireEvent.click(deleteButton);

    // Verify confirm dialog was called
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this task?');

    // Wait for async operations
    await waitFor(() => {
      expect(mockTasksService.deleteTask).toHaveBeenCalledWith(1);
      expect(mockOnDelete).toHaveBeenCalledWith(1);
    });
  });

  test('does not delete when user cancels confirmation', async () => {
    // Mock user clicking "Cancel" in confirm dialog
    window.confirm = jest.fn(() => false);

    render(
      <TaskItem
        task={mockTask}
        onUpdate={mockOnUpdate}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    const taskElement = screen.getByText('Test Task').closest('div');
    fireEvent.mouseEnter(taskElement!);

    const deleteButton = screen.getByLabelText(/delete/i) || screen.getByTitle(/delete/i);
    fireEvent.click(deleteButton);

    expect(window.confirm).toHaveBeenCalled();
    expect(mockTasksService.deleteTask).not.toHaveBeenCalled();
    expect(mockOnDelete).not.toHaveBeenCalled();
  });

  test('handles status toggle correctly', async () => {
    render(
      <TaskItem
        task={mockTask}
        onUpdate={mockOnUpdate}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    // Find the status toggle button (checkbox)
    const toggleButton = screen.getByLabelText(/mark as complete/i);
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(mockTasksService.updateTaskStatus).toHaveBeenCalledWith(1, 'completed');
      expect(mockOnUpdate).toHaveBeenCalledWith({
        ...mockTask,
        status: 'completed',
      });
      expect(mockOnComplete).toHaveBeenCalledWith(1);
    });
  });

  test('handles completed task toggle back to pending', async () => {
    const completedTask = { ...mockTask, status: 'completed' as const };
    mockTasksService.updateTaskStatus.mockResolvedValue({
      ...completedTask,
      status: 'pending',
    });

    render(
      <TaskItem
        task={completedTask}
        onUpdate={mockOnUpdate}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    const toggleButton = screen.getByLabelText(/mark as incomplete/i);
    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(mockTasksService.updateTaskStatus).toHaveBeenCalledWith(1, 'pending');
      expect(mockOnUpdate).toHaveBeenCalledWith({
        ...completedTask,
        status: 'pending',
      });
    });
  });

  test('handles API errors gracefully during deletion', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    mockTasksService.deleteTask.mockRejectedValue(new Error('API Error'));

    render(
      <TaskItem
        task={mockTask}
        onUpdate={mockOnUpdate}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    const taskElement = screen.getByText('Test Task').closest('div');
    fireEvent.mouseEnter(taskElement!);

    const deleteButton = screen.getByLabelText(/delete/i) || screen.getByTitle(/delete/i);
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockTasksService.deleteTask).toHaveBeenCalledWith(1);
      expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to delete task:', expect.any(Error));
      // onDelete should not be called if API fails
      expect(mockOnDelete).not.toHaveBeenCalled();
    });

    // Check that updating state is properly reset even on error
    const toggleButton = screen.getByLabelText(/mark as complete/i);
    expect(toggleButton).not.toBeDisabled();

    consoleErrorSpy.mockRestore();
  });
});