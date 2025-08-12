import { test, expect } from '@playwright/test';

test.describe('Frontend Homepage Snapshots', () => {
  test('homepage snapshot', async ({ page }) => {
    // Navigate to the frontend homepage
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot of the homepage
    await page.screenshot({ 
      path: 'screenshots/frontend-homepage.png',
      fullPage: true
    });
    
    // Verify the page has loaded correctly
    await expect(page).toHaveTitle(/Recaller/);
  });

  test('login page snapshot', async ({ page }) => {
    // Navigate to the login page
    await page.goto('/login');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot of the login page
    await page.screenshot({ 
      path: 'screenshots/frontend-login.png',
      fullPage: true
    });
    
    // Verify the login form is present
    await expect(page.locator('form')).toBeVisible();
  });
});