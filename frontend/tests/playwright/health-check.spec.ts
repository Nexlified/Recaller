import { test, expect } from '@playwright/test';

test.describe('Health Check', () => {
  test('frontend should be accessible', async ({ page }) => {
    await page.goto('/');
    // Basic health check - just ensure the page loads
    await expect(page).toHaveTitle(/Recaller/);
  });
});