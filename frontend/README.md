# Recaller Frontend

The frontend for Recaller - a privacy-first personal assistant app built with Next.js, TypeScript, and Tailwind CSS.

## 🚀 Tech Stack

- **Framework**: Next.js 15+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Headless UI, Heroicons
- **HTTP Client**: Axios
- **Testing**: Jest, React Testing Library, Playwright
- **Build Tool**: Turbopack (dev), Webpack (production)

## 🏁 Getting Started

### Prerequisites

- Node.js 18+ LTS
- npm, yarn, pnpm, or bun

### Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   # or
   bun install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   # or
   bun dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# Development Settings
NEXT_PUBLIC_ENV=development
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Reusable UI components
│   ├── lib/             # Utility functions and configurations
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   ├── services/        # API service functions
│   └── styles/          # Global styles and Tailwind config
├── public/              # Static assets
├── tests/               # Test files
│   └── playwright/      # End-to-end tests
├── scripts/             # Build and utility scripts
└── screenshots/         # Generated screenshots
```

## 🧪 Testing

### Unit Tests
```bash
# Run Jest tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### End-to-End Tests
```bash
# Install Playwright browsers
npx playwright install

# Run Playwright tests
npm run test:playwright

# Run tests in UI mode
npm run test:playwright:ui
```

### Screenshot Generation
```bash
# Generate screenshots manually
npm run screenshots:generate

# Validate Playwright setup
npm run validate:playwright
```

## 🔧 Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run type-check` - Run TypeScript compiler check
- `npm test` - Run unit tests
- `npm run test:playwright` - Run E2E tests
- `npm run screenshots:generate` - Generate app screenshots

## 🎨 Development Guidelines

### Code Style

- Use functional components with hooks
- Prefer TypeScript for type safety
- Follow Tailwind CSS utility-first approach
- Use meaningful component and variable names
- Write tests for new components and features

### Component Architecture

```typescript
// Example component structure
import { FC } from 'react';

interface ComponentProps {
  title: string;
  onAction: () => void;
}

export const Component: FC<ComponentProps> = ({ title, onAction }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      <button
        onClick={onAction}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Action
      </button>
    </div>
  );
};
```

### API Integration

```typescript
// Example API service
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const userService = {
  getProfile: () => api.get('/api/v1/users/me'),
  updateProfile: (data) => api.put('/api/v1/users/me', data),
};
```

## 🚀 Deployment

### Docker (Recommended)

The frontend is deployed as part of the Docker Compose stack:

```bash
# From project root
docker-compose up --build
```

### Standalone Deployment

```bash
# Build the application
npm run build

# Start production server
npm start
```

### Environment Configuration

For production deployments, set these environment variables:

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_ENV=production
```

## 🔗 Integration with Backend

The frontend communicates with the FastAPI backend via REST APIs:

- **Base URL**: `http://localhost:8000` (development)
- **API Version**: `/api/v1`
- **Authentication**: JWT tokens via Authorization header
- **Tenant Context**: `X-Tenant-ID` header for multi-tenancy

## 📚 Key Features

- **Dashboard**: Unified view of finances, reminders, and activities
- **Contact Management**: Organize and track relationships
- **Event Tracking**: Record meetings and social interactions
- **Organization Management**: Manage schools, companies, and institutions
- **Privacy-First**: No data sent to third-party services
- **Responsive Design**: Works on desktop and mobile devices
- **Multi-tenant Support**: Supports multiple organizations

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**: Change port with `npm run dev -- -p 3001`
2. **Module not found**: Clear node_modules and reinstall dependencies
3. **API connection failed**: Verify backend is running on port 8000
4. **Build errors**: Check TypeScript types and ESLint warnings

### Debug Mode

```bash
# Enable debug logging
DEBUG=* npm run dev

# Enable Next.js debug mode
NODE_OPTIONS='--inspect' npm run dev
```

## 🤝 Contributing

See our [Contributing Guide](../CONTRIBUTING.md) for development workflows and coding standards.

---

*Built with ❤️ for privacy and productivity.*
