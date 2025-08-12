# Playwright Integration Setup Guide

## Quick Start

This guide helps you set up and test the Playwright integration for Recaller.

### 1. Prerequisites

Ensure you have the following running:

- Node.js (18+)
- Python (3.13+)
- Both frontend and backend servers

### 2. Start the Servers

#### Backend (Terminal 1)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm start
```

### 3. Install Playwright

```bash
cd frontend
npm install --save-dev playwright @playwright/test
npx playwright install chromium
```

### 4. Test the Integration

#### Manual Screenshot Generation
```bash
cd frontend
node scripts/take-screenshots.js
```

#### Run Playwright Tests
```bash
cd frontend
npm run test:playwright
```

#### Health Check
```bash
cd frontend
npx playwright test tests/playwright/health-check.spec.ts --headed
```

### 5. Verify Screenshots

Check the generated screenshots in `frontend/screenshots/`:
- `frontend-homepage.png` - React app landing page
- `backend-docs.png` - FastAPI Swagger UI
- `backend-root.png` - API welcome response

### 6. MCP Integration

For Copilot integration, the MCP server configuration is already set up in `.mcp-config.json`.

### Troubleshooting

1. **Browser Installation Fails**: Try `npx playwright install --with-deps chromium`
2. **Servers Not Ready**: Wait 30 seconds after starting servers before running tests
3. **Permission Issues**: Ensure script is executable: `chmod +x scripts/take-screenshots.js`

## Environment Variables

For custom configurations:

```bash
# Optional: Custom server URLs
export FRONTEND_URL=http://localhost:3000
export BACKEND_URL=http://localhost:8000
export BACKEND_DOCS_URL=http://localhost:8000/docs
```

## GitHub Actions

The screenshot workflow runs automatically on PRs that modify frontend or backend files. No additional setup required.