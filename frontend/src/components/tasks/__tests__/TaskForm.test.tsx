import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TaskForm, TaskFormData } from '../TaskForm';
import { Task, TaskCategory } from '../../../types/Task';
import { Contact } from '../../../services/contacts';

// Mock the RecurrenceSettings component
jest.mock('../RecurrenceSettings', () => ({
  RecurrenceSettings: ({ onChange }: { onChange: (recurrence: any) => void }) => (
    <div data-testid="recurrence-settings">Recurrence Settings</div>
  ),
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
  categories: [{ id: 1, tenant_id: 1, user_id: 1, name: 'Work', created_at: '2024-01-01T00:00:00Z' }],
  contacts: [{ id: 1, first_name: 'John', last_name: 'Doe', email: 'john@example.com' }],
};

const mockCategories: TaskCategory[] = [
  { id: 1, tenant_id: 1, user_id: 1, name: 'Work', created_at: '2024-01-01T00:00:00Z' },
  { id: 2, tenant_id: 1, user_id: 1, name: 'Personal', created_at: '2024-01-01T00:00:00Z' },
];

const mockContacts: Contact[] = [
  { id: 1, first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
  { id: 2, first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' },
];

describe('TaskForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form for creating new task', () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    expect(screen.getByText('Create New Task')).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByText('Create Task')).toBeInTheDocument();
  });

  test('renders form for editing existing task', () => {
    render(
      <TaskForm
        task={mockTask}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    expect(screen.getByText('Edit Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test Description')).toBeInTheDocument();
    expect(screen.getByText('Update Task')).toBeInTheDocument();
  });

  test('submits form with correct data for create', async () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    const titleInput = screen.getByLabelText(/title/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByText('Create Task');

    fireEvent.change(titleInput, { target: { value: 'New Task' } });
    fireEvent.change(descriptionInput, { target: { value: 'New Description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        core: expect.objectContaining({
          title: 'New Task',
          description: 'New Description',
          status: 'pending',
          priority: 'medium',
          category_ids: [],
          contact_ids: [],
        }),
      });
    });
  });

  test('submits form with correct data for edit', async () => {
    render(
      <TaskForm
        task={mockTask}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    const titleInput = screen.getByDisplayValue('Test Task');
    const submitButton = screen.getByText('Update Task');

    fireEvent.change(titleInput, { target: { value: 'Updated Task' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        core: expect.objectContaining({
          title: 'Updated Task',
          description: 'Test Description',
          status: 'pending',
          priority: 'medium',
        }),
        associations: expect.objectContaining({
          category_ids: [1],
          contact_ids: [1],
        }),
      });
    });
  });

  test('validates required title field', async () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    const submitButton = screen.getByText('Create Task');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Title is required')).toBeInTheDocument();
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });
  });

  test('handles category selection', async () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    const workCategoryButton = screen.getByText('Work');
    fireEvent.click(workCategoryButton);

    const titleInput = screen.getByLabelText(/title/i);
    const submitButton = screen.getByText('Create Task');

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        core: expect.objectContaining({
          category_ids: [1],
        }),
      });
    });
  });

  test('handles contact selection', async () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    const johnContactButton = screen.getByText('👤 John Doe');
    fireEvent.click(johnContactButton);

    const titleInput = screen.getByLabelText(/title/i);
    const submitButton = screen.getByText('Create Task');

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        core: expect.objectContaining({
          contact_ids: [1],
        }),
      });
    });
  });

  test('calls onCancel when cancel button is clicked', () => {
    render(
      <TaskForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  test('formats dates correctly for datetime-local input', () => {
    render(
      <TaskForm
        task={mockTask}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        categories={mockCategories}
        contacts={mockContacts}
      />
    );

    const startDateInput = screen.getByLabelText(/start date/i);
    const dueDateInput = screen.getByLabelText(/due date/i);

    // Check that dates are formatted correctly for datetime-local input
    expect(startDateInput).toHaveValue('2024-01-01T10:00');
    expect(dueDateInput).toHaveValue('2024-01-02T10:00');
  });
});