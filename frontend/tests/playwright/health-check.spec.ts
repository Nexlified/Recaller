const { test, expect } = require('@playwright/test');

test.describe('Health Check Tests', () => {
  test('frontend is accessible', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await expect(page).toHaveTitle(/React App|Recaller/);
  });

  test('backend is accessible', async ({ page }) => {
    await page.goto('http://localhost:8000');
    await expect(page.locator('body')).toContainText('Welcome to Recaller API');
  });

  test('backend docs are accessible', async ({ page }) => {
    await page.goto('http://localhost:8000/docs');
    await expect(page).toHaveTitle(/Recaller/);
  });
});