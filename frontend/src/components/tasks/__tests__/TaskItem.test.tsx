import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskItem } from '../TaskItem';
import { mockTask, mockCompletedTask, mockOverdueTask } from '../../../__mocks__/taskMocks';
import tasksService from '../../../services/tasks';

// Mock the tasks service
jest.mock('../../../services/tasks', () => ({
  updateTaskStatus: jest.fn(),
  deleteTask: jest.fn(),
  isTaskOverdue: jest.fn(),
}));

// Mock the child components
jest.mock('../TaskStatusBadge', () => ({
  TaskStatusBadge: ({ status }: { status: string }) => <span data-testid={`status-badge-${status}`}>{status}</span>,
}));

jest.mock('../TaskPriorityBadge', () => ({
  TaskPriorityBadge: ({ priority }: { priority: string }) => <span data-testid={`priority-badge-${priority}`}>{priority}</span>,
}));

jest.mock('../DueDateIndicator', () => ({
  DueDateIndicator: ({ dueDate }: { dueDate: string }) => <span data-testid="due-date-indicator">{dueDate}</span>,
}));

const mockTasksService = tasksService as jest.Mocked<typeof tasksService>;

describe('TaskItem', () => {
  const mockOnUpdate = jest.fn();
  const mockOnDelete = jest.fn();
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockTasksService.isTaskOverdue.mockReturnValue(false);
  });

  const defaultProps = {
    task: mockTask,
    onUpdate: mockOnUpdate,
    onDelete: mockOnDelete,
    onComplete: mockOnComplete,
  };

  describe('Rendering', () => {
    it('renders task title and description', () => {
      render(<TaskItem {...defaultProps} />);
      
      expect(screen.getByText(mockTask.title)).toBeInTheDocument();
      expect(screen.getByText(mockTask.description!)).toBeInTheDocument();
    });

    it('renders task priority badge', () => {
      render(<TaskItem {...defaultProps} />);
      
      expect(screen.getByTestId(`priority-badge-${mockTask.priority}`)).toBeInTheDocument();
    });

    it('renders due date indicator when task has due date', () => {
      render(<TaskItem {...defaultProps} />);
      
      expect(screen.getByTestId('due-date-indicator')).toBeInTheDocument();
    });

    it('does not render due date indicator when task has no due date', () => {
      const taskWithoutDueDate = { ...mockTask, due_date: undefined };
      render(<TaskItem {...defaultProps} task={taskWithoutDueDate} />);
      
      expect(screen.queryByTestId('due-date-indicator')).not.toBeInTheDocument();
    });

    it('renders compact view when compact prop is true', () => {
      render(<TaskItem {...defaultProps} compact={true} />);
      
      // In compact view, title should be smaller and description might not be shown
      const titleElement = screen.getByText(mockTask.title);
      expect(titleElement).toHaveClass('text-sm');
    });

    it('applies custom className', () => {
      const customClass = 'custom-task-item';
      const { container } = render(<TaskItem {...defaultProps} className={customClass} />);
      
      expect(container.firstChild).toHaveClass(customClass);
    });
  });

  describe('Task Status', () => {
    it('shows completed state for completed tasks', () => {
      render(<TaskItem {...defaultProps} task={mockCompletedTask} />);
      
      const titleElement = screen.getByText(mockCompletedTask.title);
      expect(titleElement).toHaveClass('line-through');
      expect(titleElement).toHaveClass('text-gray-500');
    });

    it('shows pending state for pending tasks', () => {
      render(<TaskItem {...defaultProps} />);
      
      const titleElement = screen.getByText(mockTask.title);
      expect(titleElement).not.toHaveClass('line-through');
    });

    it('displays correct checkbox state for completed tasks', () => {
      render(<TaskItem {...defaultProps} task={mockCompletedTask} />);
      
      const checkbox = screen.getByRole('button', { name: /mark as incomplete/i });
      expect(checkbox.querySelector('div')).toHaveClass('bg-green-500');
    });

    it('displays correct checkbox state for pending tasks', () => {
      render(<TaskItem {...defaultProps} />);
      
      const checkbox = screen.getByRole('button', { name: /mark as complete/i });
      expect(checkbox.querySelector('div')).toHaveClass('border-gray-300');
    });
  });

  describe('Interactions', () => {
    it('toggles completion status when checkbox clicked', async () => {
      const user = userEvent.setup();
      const updatedTask = { ...mockTask, status: 'completed' as const };
      mockTasksService.updateTaskStatus.mockResolvedValue(updatedTask);
      
      render(<TaskItem {...defaultProps} />);
      
      const checkbox = screen.getByRole('button', { name: /mark as complete/i });
      await user.click(checkbox);
      
      await waitFor(() => {
        expect(mockTasksService.updateTaskStatus).toHaveBeenCalledWith(mockTask.id, 'completed');
        expect(mockOnUpdate).toHaveBeenCalledWith(updatedTask);
        expect(mockOnComplete).toHaveBeenCalledWith(mockTask.id);
      });
    });

    it('toggles from completed to pending when checkbox clicked', async () => {
      const user = userEvent.setup();
      const updatedTask = { ...mockCompletedTask, status: 'pending' as const };
      mockTasksService.updateTaskStatus.mockResolvedValue(updatedTask);
      
      render(<TaskItem {...defaultProps} task={mockCompletedTask} />);
      
      const checkbox = screen.getByRole('button', { name: /mark as incomplete/i });
      await user.click(checkbox);
      
      await waitFor(() => {
        expect(mockTasksService.updateTaskStatus).toHaveBeenCalledWith(mockCompletedTask.id, 'pending');
        expect(mockOnUpdate).toHaveBeenCalledWith(updatedTask);
        expect(mockOnComplete).not.toHaveBeenCalled();
      });
    });

    it('shows delete button on hover', async () => {
      const user = userEvent.setup();
      render(<TaskItem {...defaultProps} compact={true} />);
      
      const taskItem = screen.getByText(mockTask.title).closest('div');
      expect(screen.queryByRole('button', { name: /delete task/i })).not.toBeInTheDocument();
      
      if (taskItem) {
        await user.hover(taskItem);
        expect(screen.getByRole('button', { name: /delete task/i })).toBeInTheDocument();
      }
    });

    it('deletes task when delete button clicked and confirmed', async () => {
      const user = userEvent.setup();
      // Mock window.confirm to return true
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
      mockTasksService.deleteTask.mockResolvedValue();
      
      render(<TaskItem {...defaultProps} compact={true} />);
      
      // First hover to show the delete button
      const taskItem = screen.getByText(mockTask.title).closest('div');
      if (taskItem) {
        await user.hover(taskItem);
      }
      
      const deleteButton = screen.getByRole('button', { name: /delete task/i });
      await user.click(deleteButton);
      
      await waitFor(() => {
        expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this task?');
        expect(mockTasksService.deleteTask).toHaveBeenCalledWith(mockTask.id);
        expect(mockOnDelete).toHaveBeenCalledWith(mockTask.id);
      });
      
      confirmSpy.mockRestore();
    });

    it('does not delete task when deletion is not confirmed', async () => {
      const user = userEvent.setup();
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false);
      
      render(<TaskItem {...defaultProps} compact={true} />);
      
      // First hover to show the delete button
      const taskItem = screen.getByText(mockTask.title).closest('div');
      if (taskItem) {
        await user.hover(taskItem);
      }
      
      const deleteButton = screen.getByRole('button', { name: /delete task/i });
      await user.click(deleteButton);
      
      expect(confirmSpy).toHaveBeenCalled();
      expect(mockTasksService.deleteTask).not.toHaveBeenCalled();
      expect(mockOnDelete).not.toHaveBeenCalled();
      
      confirmSpy.mockRestore();
    });
  });

  describe('Error Handling', () => {
    it('handles error when updating task status fails', async () => {
      const user = userEvent.setup();
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      mockTasksService.updateTaskStatus.mockRejectedValue(new Error('API Error'));
      
      render(<TaskItem {...defaultProps} />);
      
      const checkbox = screen.getByRole('button', { name: /mark as complete/i });
      await user.click(checkbox);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to update task status:', expect.any(Error));
      });
      
      consoleSpy.mockRestore();
    });

    it('handles error when deleting task fails', async () => {
      const user = userEvent.setup();
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      mockTasksService.deleteTask.mockRejectedValue(new Error('API Error'));
      
      render(<TaskItem {...defaultProps} compact={true} />);
      
      // First hover to show the delete button
      const taskItem = screen.getByText(mockTask.title).closest('div');
      if (taskItem) {
        await user.hover(taskItem);
      }
      
      const deleteButton = screen.getByRole('button', { name: /delete task/i });
      await user.click(deleteButton);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to delete task:', expect.any(Error));
      });
      
      confirmSpy.mockRestore();
      consoleSpy.mockRestore();
    });
  });

  describe('Loading States', () => {
    it('disables checkbox when updating', async () => {
      const user = userEvent.setup();
      // Make the update promise pending
      mockTasksService.updateTaskStatus.mockImplementation(() => new Promise(() => {}));
      
      render(<TaskItem {...defaultProps} />);
      
      const checkbox = screen.getByRole('button', { name: /mark as complete/i });
      await user.click(checkbox);
      
      expect(checkbox).toBeDisabled();
    });

    it('disables delete button when updating', async () => {
      const user = userEvent.setup();
      jest.spyOn(window, 'confirm').mockReturnValue(true);
      // Make the delete promise pending
      mockTasksService.deleteTask.mockImplementation(() => new Promise(() => {}));
      
      render(<TaskItem {...defaultProps} compact={true} />);
      
      // First hover to show the delete button
      const taskItem = screen.getByText(mockTask.title).closest('div');
      if (taskItem) {
        await user.hover(taskItem);
      }
      
      const deleteButton = screen.getByRole('button', { name: /delete task/i });
      await user.click(deleteButton);
      
      expect(deleteButton).toBeDisabled();
    });
  });

  describe('Overdue Tasks', () => {
    it('shows overdue status for past due date', () => {
      mockTasksService.isTaskOverdue.mockReturnValue(true);
      render(<TaskItem {...defaultProps} task={mockOverdueTask} />);
      
      // The component should render with overdue styling
      // This depends on how the component handles overdue tasks
      expect(mockTasksService.isTaskOverdue).toHaveBeenCalledWith(mockOverdueTask);
    });
  });
});