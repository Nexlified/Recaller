#!/usr/bin/env node

/**
 * Screenshot Generation Script for Recaller
 * 
 * This script takes screenshots of the frontend homepage and backend docs
 * for use in PRs and documentation.
 * 
 * Usage:
 *   node scripts/take-screenshots.js
 * 
 * Requirements:
 *   - Frontend server running on http://localhost:3000
 *   - Backend server running on http://localhost:8000
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_DOCS_URL = 'http://localhost:8000/docs';
const BACKEND_ROOT_URL = 'http://localhost:8000';
const SCREENSHOTS_DIR = path.join(__dirname, '..', 'screenshots');

// Ensure screenshots directory exists
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function takeScreenshots() {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  try {
    console.log('📸 Taking screenshots for Recaller...');

    // Frontend Homepage
    console.log('🏠 Capturing frontend homepage...');
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, 'frontend-homepage.png'),
      fullPage: true
    });
    console.log('✅ Frontend homepage captured');

    // Backend Docs
    console.log('📚 Capturing backend docs...');
    await page.goto(BACKEND_DOCS_URL);
    await page.waitForLoadState('networkidle');
    // Wait a bit for Swagger UI to render
    await page.waitForTimeout(2000);
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, 'backend-docs.png'),
      fullPage: true
    });
    console.log('✅ Backend docs captured');

    // Backend Root
    console.log('🌐 Capturing backend root endpoint...');
    await page.goto(BACKEND_ROOT_URL);
    await page.waitForLoadState('networkidle');
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, 'backend-root.png'),
      fullPage: true
    });
    console.log('✅ Backend root endpoint captured');

    console.log('🎉 All screenshots captured successfully!');
    console.log(`📁 Screenshots saved to: ${SCREENSHOTS_DIR}`);

  } catch (error) {
    console.error('❌ Error taking screenshots:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Run if this script is executed directly
if (require.main === module) {
  takeScreenshots().catch(error => {
    console.error('Failed to take screenshots:', error);
    process.exit(1);
  });
}

module.exports = { takeScreenshots };