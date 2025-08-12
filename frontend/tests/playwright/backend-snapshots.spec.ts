import { test, expect } from '@playwright/test';

test.describe('Backend API Documentation Snapshots', () => {
  test('backend docs snapshot', async ({ page }) => {
    // Navigate to the backend docs page
    await page.goto('http://localhost:8000/docs');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    
    // Wait for the Swagger UI to render
    await page.waitForSelector('.swagger-ui', { timeout: 10000 });
    
    // Take a screenshot of the API docs
    await page.screenshot({ 
      path: 'screenshots/backend-docs.png',
      fullPage: true
    });
    
    // Verify the API docs page has loaded
    await expect(page.locator('.swagger-ui')).toBeVisible();
    await expect(page).toHaveTitle(/FastAPI/);
  });

  test('backend root endpoint snapshot', async ({ page }) => {
    // Navigate to the backend root endpoint
    await page.goto('http://localhost:8000/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot of the root API response
    await page.screenshot({ 
      path: 'screenshots/backend-root.png',
      fullPage: true
    });
    
    // Verify the API response contains expected content
    await expect(page.locator('body')).toContainText('Welcome to Recaller API');
  });
});