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

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
    try {
      await page.goto(FRONTEND_URL, { waitUntil: 'networkidle', timeout: 30000 });
      await page.screenshot({
        path: path.join(SCREENSHOTS_DIR, 'frontend-homepage.png'),
        fullPage: true
      });
      console.log('✅ Frontend homepage captured');
    } catch (error) {
      console.error('❌ Failed to capture frontend homepage:', error.message);
      // Continue with other screenshots
    }

    // Backend Docs
    console.log('📚 Capturing backend docs...');
    try {
      await page.goto(BACKEND_DOCS_URL, { waitUntil: 'networkidle', timeout: 30000 });
      // Wait a bit for Swagger UI to render
      await page.waitForTimeout(3000);
      await page.screenshot({
        path: path.join(SCREENSHOTS_DIR, 'backend-docs.png'),
        fullPage: true
      });
      console.log('✅ Backend docs captured');
    } catch (error) {
      console.error('❌ Failed to capture backend docs:', error.message);
      // Continue with other screenshots
    }

    // Backend Root
    console.log('🌐 Capturing backend root endpoint...');
    try {
      await page.goto(BACKEND_ROOT_URL, { waitUntil: 'networkidle', timeout: 30000 });
      await page.screenshot({
        path: path.join(SCREENSHOTS_DIR, 'backend-root.png'),
        fullPage: true
      });
      console.log('✅ Backend root endpoint captured');
    } catch (error) {
      console.error('❌ Failed to capture backend root:', error.message);
      // Continue
    }

    // Check if any screenshots were taken
    const screenshots = fs.readdirSync(SCREENSHOTS_DIR).filter(file => file.endsWith('.png'));
    if (screenshots.length === 0) {
      console.error('❌ No screenshots were captured successfully');
      process.exit(1);
    }

    console.log('🎉 Screenshots captured successfully!');
    console.log(`📁 Screenshots saved to: ${SCREENSHOTS_DIR}`);
    console.log(`📊 Total screenshots: ${screenshots.length}`);

  } catch (error) {
    console.error('❌ Error taking screenshots:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Run if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  takeScreenshots().catch(error => {
    console.error('Failed to take screenshots:', error);
    process.exit(1);
  });
}

export { takeScreenshots };
