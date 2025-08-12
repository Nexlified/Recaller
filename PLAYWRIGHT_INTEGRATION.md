# Playwright Integration for Recaller

This document describes the Playwright integration for automated screenshot generation and testing in the Recaller project.

## Overview

The Playwright integration provides:

- **Automated screenshot generation** for frontend homepage and backend documentation
- **PR screenshot attachments** via GitHub Actions
- **MCP server integration** for Copilot screenshot capabilities
- **Local development tools** for manual screenshot generation

## Files Added/Modified

### Frontend Package Changes
- `frontend/package.json` - Added Playwright dependencies and scripts
- `frontend/playwright.config.ts` - Playwright configuration
- `frontend/tests/playwright/` - Playwright test files
- `frontend/scripts/take-screenshots.js` - Screenshot generation script
- `frontend/screenshots/` - Generated screenshots directory

### GitHub Actions
- `.github/workflows/screenshots.yml` - PR screenshot workflow

### Configuration
- `.mcp-config.json` - MCP server configuration for Copilot

## Usage

### Manual Screenshot Generation

Generate screenshots locally:

```bash
cd frontend

# Start both servers (in separate terminals)
npm start                    # Frontend on :3000
cd ../backend && uvicorn app.main:app --reload  # Backend on :8000

# Generate screenshots
npm run screenshots:generate
```

### Playwright Tests

Run Playwright tests:

```bash
cd frontend

# Run all Playwright tests
npm run test:playwright

# Run only screenshot tests
npm run test:screenshots

# Run frontend screenshots only
npm run screenshots:frontend

# Run backend screenshots only
npm run screenshots:backend
```

### GitHub Actions Integration

Screenshots are automatically generated and attached to PRs when:
- Changes are made to `frontend/` or `backend/` directories
- The PR is opened or updated
- The workflow file is modified

The workflow will:
1. Start both frontend and backend servers
2. Generate screenshots using Playwright
3. Upload screenshots as artifacts
4. Comment on the PR with screenshot previews

### MCP Server Integration

For Copilot integration, the MCP server configuration is provided in `.mcp-config.json`. This allows Copilot to:
- Take screenshots during development
- Attach screenshots to PRs
- Provide visual feedback during code reviews

## Configuration

### Playwright Configuration

The main configuration is in `frontend/playwright.config.ts`:

```typescript
export default defineConfig({
  testDir: './tests/playwright',
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: [
    {
      command: 'npm start',
      port: 3000,
    },
    {
      command: 'cd ../backend && uvicorn app.main:app --host 0.0.0.0 --port 8000',
      port: 8000,
    }
  ],
});
```

### Screenshot Targets

The following pages are captured:

1. **Frontend Homepage** (`http://localhost:3000/`)
   - Main application landing page
   - Full page screenshot

2. **Backend API Documentation** (`http://localhost:8000/docs`)
   - FastAPI Swagger UI documentation
   - Full page screenshot

3. **Backend Root Endpoint** (`http://localhost:8000/`)
   - API welcome message
   - JSON response view

## Development

### Adding New Screenshot Targets

To add new pages for screenshot capture:

1. Add new test cases in `frontend/tests/playwright/`
2. Update the screenshot script in `frontend/scripts/take-screenshots.js`
3. Modify the GitHub Actions workflow if needed

Example test case:

```typescript
test('new page snapshot', async ({ page }) => {
  await page.goto('/new-page');
  await page.waitForLoadState('networkidle');
  await page.screenshot({ 
    path: 'screenshots/new-page.png',
    fullPage: true
  });
});
```

### Customizing Screenshot Settings

Screenshot behavior can be customized by modifying:

- **Viewport size**: Set in playwright.config.ts or individual tests
- **Wait conditions**: Adjust `waitForLoadState` or add custom waits
- **File naming**: Update paths in test files and scripts
- **Image format**: Change from PNG to JPEG if needed

## Troubleshooting

### Common Issues

1. **Servers not running**: Ensure both frontend (3000) and backend (8000) are accessible
2. **Playwright browser installation**: Run `npx playwright install` if browsers are missing
3. **Network timeouts**: Increase timeout values in playwright.config.ts
4. **Screenshot directory**: Ensure `frontend/screenshots/` directory exists

### Environment Variables

For CI/CD environments, these variables may be needed:

```bash
# Backend database connection
POSTGRES_SERVER=localhost
POSTGRES_USER=recaller
POSTGRES_PASSWORD=recaller
POSTGRES_DB=recaller

# Optional: Custom URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## Integration with MCP

The MCP (Model Context Protocol) integration allows Copilot to:

1. **Take screenshots** during development sessions
2. **Attach visual context** to PR reviews
3. **Document UI changes** automatically
4. **Provide visual regression detection**

This enhances the development workflow by providing visual feedback and documentation automatically.