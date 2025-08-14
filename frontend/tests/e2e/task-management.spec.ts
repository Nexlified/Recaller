import { test, expect } from '@playwright/test';

test.describe('Task Management E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page and authenticate
    await page.goto('/login');
    
    // Fill login form
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('[data-testid=submit]');
    
    // Wait for successful login and redirect to dashboard
    await page.waitForURL('/dashboard');
    await expect(page).toHaveURL('/dashboard');
  });

  test('creates and manages tasks end-to-end', async ({ page }) => {
    // Navigate to tasks page
    await page.click('[data-testid=nav-tasks]');
    await page.waitForURL('/tasks');
    await expect(page).toHaveURL('/tasks');

    // Create a new task
    await page.click('[data-testid=create-task]');
    await page.waitForSelector('[data-testid=task-form]');

    // Fill task form
    await page.fill('[data-testid=task-title]', 'E2E Test Task');
    await page.fill('[data-testid=task-description]', 'This is an end-to-end test task');
    await page.selectOption('[data-testid=task-priority]', 'high');
    
    // Set due date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid=task-due-date]', tomorrowStr);

    // Submit the form
    await page.click('[data-testid=submit-task]');

    // Verify task appears in the list
    await page.waitForSelector('[data-testid=task-list]');
    await expect(page.locator('[data-testid=task-item]')).toContainText('E2E Test Task');
    
    // Verify task details are displayed correctly
    const taskItem = page.locator('[data-testid=task-item]').filter({ hasText: 'E2E Test Task' });
    await expect(taskItem).toContainText('This is an end-to-end test task');
    await expect(taskItem).toContainText('High'); // Priority badge
    
    // Complete the task
    await taskItem.locator('[data-testid=task-checkbox]').click();
    
    // Verify task is marked as completed
    await expect(taskItem).toHaveClass(/completed/);
    await expect(taskItem.locator('h3')).toHaveClass(/line-through/);

    // Filter to show only completed tasks
    await page.selectOption('[data-testid=status-filter]', 'completed');
    
    // Verify the completed task is still visible
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'E2E Test Task' })).toBeVisible();
    
    // Filter to show only pending tasks
    await page.selectOption('[data-testid=status-filter]', 'pending');
    
    // Verify the completed task is no longer visible
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'E2E Test Task' })).not.toBeVisible();
  });

  test('task board view works correctly', async ({ page }) => {
    // Navigate to task board
    await page.goto('/tasks/board');
    await expect(page).toHaveURL('/tasks/board');

    // Verify board columns are present
    await expect(page.locator('[data-testid=column-pending]')).toBeVisible();
    await expect(page.locator('[data-testid=column-in-progress]')).toBeVisible();
    await expect(page.locator('[data-testid=column-completed]')).toBeVisible();

    // Verify column headers
    await expect(page.locator('[data-testid=column-pending]')).toContainText('Pending');
    await expect(page.locator('[data-testid=column-in-progress]')).toContainText('In Progress');
    await expect(page.locator('[data-testid=column-completed]')).toContainText('Completed');

    // Create a task that will appear in pending column
    await page.click('[data-testid=quick-add-task]');
    await page.fill('[data-testid=quick-task-input]', 'Board Test Task');
    await page.click('[data-testid=quick-task-submit]');

    // Verify task appears in pending column
    const pendingColumn = page.locator('[data-testid=column-pending]');
    await expect(pendingColumn.locator('[data-testid=task-card]').filter({ hasText: 'Board Test Task' })).toBeVisible();

    // Test drag and drop functionality (if implemented)
    const taskCard = pendingColumn.locator('[data-testid=task-card]').filter({ hasText: 'Board Test Task' });
    const inProgressColumn = page.locator('[data-testid=column-in-progress]');
    
    // Note: Drag and drop testing depends on implementation
    // await taskCard.dragTo(inProgressColumn);
    // await expect(inProgressColumn.locator('[data-testid=task-card]').filter({ hasText: 'Board Test Task' })).toBeVisible();
  });

  test('category management workflow', async ({ page }) => {
    // Navigate to task categories
    await page.goto('/tasks/categories');
    await expect(page).toHaveURL('/tasks/categories');

    // Create a new category
    await page.click('[data-testid=create-category]');
    await page.waitForSelector('[data-testid=category-form]');

    // Fill category form
    await page.fill('[data-testid=category-name]', 'E2E Test Category');
    await page.fill('[data-testid=category-description]', 'Category for E2E testing');
    
    // Select a color
    await page.click('[data-testid=color-picker-blue]');
    
    // Submit the form
    await page.click('[data-testid=submit-category]');

    // Verify category appears in the list
    await expect(page.locator('[data-testid=category-item]').filter({ hasText: 'E2E Test Category' })).toBeVisible();

    // Edit the category
    const categoryItem = page.locator('[data-testid=category-item]').filter({ hasText: 'E2E Test Category' });
    await categoryItem.locator('[data-testid=edit-category]').click();

    // Update category name
    await page.fill('[data-testid=category-name]', 'Updated E2E Category');
    await page.click('[data-testid=submit-category]');

    // Verify category name is updated
    await expect(page.locator('[data-testid=category-item]').filter({ hasText: 'Updated E2E Category' })).toBeVisible();
    await expect(page.locator('[data-testid=category-item]').filter({ hasText: 'E2E Test Category' })).not.toBeVisible();

    // Delete the category
    await categoryItem.locator('[data-testid=delete-category]').click();
    
    // Confirm deletion
    await page.click('[data-testid=confirm-delete]');

    // Verify category is removed
    await expect(page.locator('[data-testid=category-item]').filter({ hasText: 'Updated E2E Category' })).not.toBeVisible();
  });

  test('task filters and search functionality', async ({ page }) => {
    // Navigate to tasks page
    await page.goto('/tasks');

    // Create multiple tasks with different properties for testing filters
    const testTasks = [
      { title: 'High Priority Task', priority: 'high', status: 'pending' },
      { title: 'Low Priority Task', priority: 'low', status: 'completed' },
      { title: 'Medium Priority Task', priority: 'medium', status: 'in_progress' },
      { title: 'Searchable Task with Keywords', priority: 'medium', status: 'pending' }
    ];

    for (const task of testTasks) {
      await page.click('[data-testid=create-task]');
      await page.fill('[data-testid=task-title]', task.title);
      await page.selectOption('[data-testid=task-priority]', task.priority);
      await page.selectOption('[data-testid=task-status]', task.status);
      await page.click('[data-testid=submit-task]');
      
      // Wait for task to appear
      await expect(page.locator('[data-testid=task-item]').filter({ hasText: task.title })).toBeVisible();
    }

    // Test priority filter
    await page.selectOption('[data-testid=priority-filter]', 'high');
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'High Priority Task' })).toBeVisible();
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'Low Priority Task' })).not.toBeVisible();

    // Reset filters
    await page.selectOption('[data-testid=priority-filter]', 'all');

    // Test status filter
    await page.selectOption('[data-testid=status-filter]', 'completed');
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'Low Priority Task' })).toBeVisible();
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'High Priority Task' })).not.toBeVisible();

    // Reset filters
    await page.selectOption('[data-testid=status-filter]', 'all');

    // Test search functionality
    await page.fill('[data-testid=search-input]', 'Keywords');
    await page.press('[data-testid=search-input]', 'Enter');
    
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'Searchable Task with Keywords' })).toBeVisible();
    await expect(page.locator('[data-testid=task-item]').filter({ hasText: 'High Priority Task' })).not.toBeVisible();

    // Clear search
    await page.fill('[data-testid=search-input]', '');
    await page.press('[data-testid=search-input]', 'Enter');
    
    // Verify all tasks are visible again
    await expect(page.locator('[data-testid=task-item]')).toHaveCount(4);
  });

  test('task dashboard displays correct metrics', async ({ page }) => {
    // Go to task dashboard
    await page.goto('/tasks');

    // Create test data with known quantities
    const testData = [
      { title: 'Pending Task 1', status: 'pending', priority: 'high' },
      { title: 'Pending Task 2', status: 'pending', priority: 'medium' },
      { title: 'Completed Task 1', status: 'completed', priority: 'low' },
      { title: 'In Progress Task 1', status: 'in_progress', priority: 'high' }
    ];

    // Create the test tasks
    for (const task of testData) {
      await page.click('[data-testid=create-task]');
      await page.fill('[data-testid=task-title]', task.title);
      await page.selectOption('[data-testid=task-priority]', task.priority);
      if (task.status !== 'pending') {
        await page.selectOption('[data-testid=task-status]', task.status);
      }
      await page.click('[data-testid=submit-task]');
    }

    // Verify dashboard metrics
    await expect(page.locator('[data-testid=total-tasks-count]')).toContainText('4');
    await expect(page.locator('[data-testid=pending-tasks-count]')).toContainText('2');
    await expect(page.locator('[data-testid=completed-tasks-count]')).toContainText('1');
    await expect(page.locator('[data-testid=in-progress-tasks-count]')).toContainText('1');

    // Verify high priority tasks count
    await expect(page.locator('[data-testid=high-priority-count]')).toContainText('2');
  });

  test('recurring task creation and management', async ({ page }) => {
    // Navigate to recurring tasks
    await page.goto('/tasks/recurring');

    // Create a recurring task
    await page.click('[data-testid=create-recurring-task]');
    
    // Fill basic task information
    await page.fill('[data-testid=task-title]', 'Weekly Standup');
    await page.fill('[data-testid=task-description]', 'Team standup meeting');
    
    // Set recurrence pattern
    await page.selectOption('[data-testid=recurrence-type]', 'weekly');
    await page.fill('[data-testid=recurrence-interval]', '1');
    
    // Select days of week (Monday, Wednesday, Friday)
    await page.check('[data-testid=day-monday]');
    await page.check('[data-testid=day-wednesday]');
    await page.check('[data-testid=day-friday]');
    
    // Set lead time
    await page.fill('[data-testid=lead-time-days]', '1');
    
    // Submit the form
    await page.click('[data-testid=submit-recurring-task]');

    // Verify recurring task appears in the list
    await expect(page.locator('[data-testid=recurring-task-item]').filter({ hasText: 'Weekly Standup' })).toBeVisible();
    
    // Verify recurrence pattern is displayed
    const recurringTaskItem = page.locator('[data-testid=recurring-task-item]').filter({ hasText: 'Weekly Standup' });
    await expect(recurringTaskItem).toContainText('Weekly');
    await expect(recurringTaskItem).toContainText('Mon, Wed, Fri');

    // Edit the recurring task
    await recurringTaskItem.locator('[data-testid=edit-recurring-task]').click();
    
    // Change to daily recurrence
    await page.selectOption('[data-testid=recurrence-type]', 'daily');
    await page.fill('[data-testid=recurrence-interval]', '2'); // Every 2 days
    
    await page.click('[data-testid=submit-recurring-task]');

    // Verify changes are reflected
    await expect(recurringTaskItem).toContainText('Every 2 days');
  });

  test('task calendar view functionality', async ({ page }) => {
    // Navigate to task calendar
    await page.goto('/tasks/calendar');
    await expect(page).toHaveURL('/tasks/calendar');

    // Verify calendar is displayed
    await expect(page.locator('[data-testid=calendar-view]')).toBeVisible();
    
    // Verify navigation buttons
    await expect(page.locator('[data-testid=calendar-prev]')).toBeVisible();
    await expect(page.locator('[data-testid=calendar-next]')).toBeVisible();
    await expect(page.locator('[data-testid=calendar-today]')).toBeVisible();

    // Create a task with a specific due date
    await page.click('[data-testid=add-task-calendar]');
    
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    
    await page.fill('[data-testid=task-title]', 'Calendar Task');
    await page.fill('[data-testid=task-due-date]', tomorrowStr);
    await page.click('[data-testid=submit-task]');

    // Verify task appears on the calendar
    const tomorrowDay = page.locator(`[data-testid=calendar-day-${tomorrowStr}]`);
    await expect(tomorrowDay.locator('[data-testid=calendar-task]').filter({ hasText: 'Calendar Task' })).toBeVisible();

    // Click on the task in calendar to view details
    await tomorrowDay.locator('[data-testid=calendar-task]').filter({ hasText: 'Calendar Task' }).click();
    
    // Verify task details modal opens
    await expect(page.locator('[data-testid=task-details-modal]')).toBeVisible();
    await expect(page.locator('[data-testid=task-details-title]')).toContainText('Calendar Task');
  });

  test('handles errors gracefully', async ({ page }) => {
    // Navigate to tasks page
    await page.goto('/tasks');

    // Test form validation errors
    await page.click('[data-testid=create-task]');
    
    // Try to submit empty form
    await page.click('[data-testid=submit-task]');
    
    // Verify validation error appears
    await expect(page.locator('[data-testid=error-message]')).toContainText('Title is required');

    // Test network error handling (mock offline)
    await page.route('**/api/v1/tasks/**', route => route.abort());
    
    // Try to create a task
    await page.fill('[data-testid=task-title]', 'Test Task');
    await page.click('[data-testid=submit-task]');
    
    // Verify error message is displayed
    await expect(page.locator('[data-testid=error-notification]')).toContainText('Failed to create task');
  });
});