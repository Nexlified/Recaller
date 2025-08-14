# Task Management Testing Suite

This comprehensive testing suite covers all aspects of the task management system in Recaller, providing thorough validation of functionality, performance, and user experience.

## Overview

The testing infrastructure includes:

- **Frontend Component Tests** - React component testing with React Testing Library
- **Frontend Hook Tests** - Custom hook testing for state management
- **Frontend Page Tests** - Integration testing for page components
- **Backend API Tests** - Comprehensive API endpoint testing
- **Backend Integration Tests** - Full workflow testing
- **Performance Tests** - Load and stress testing
- **End-to-End Tests** - Complete user journey testing with Playwright
- **CI/CD Integration** - Automated testing pipeline

## Test Coverage

### Frontend Testing

#### Component Tests (`frontend/src/components/tasks/__tests__/`)

- **TaskItem.test.tsx** - Tests for individual task items
  - Rendering task information
  - Status toggling (pending ↔ completed)
  - Priority and due date display
  - Delete functionality
  - Error handling
  - Loading states

- **TaskList.test.tsx** - Tests for task list component
- **TaskForm.test.tsx** - Tests for task creation/editing forms
- **TaskFilters.test.tsx** - Tests for filtering components

#### Hook Tests (`frontend/src/hooks/__tests__/`)

- **useTasks.test.ts** - Tests for task management hooks
  - Context provider validation
  - CRUD operations (create, read, update, delete)
  - Error handling
  - Loading states
  - Task selectors (pending, completed, overdue, etc.)
  - Filtering logic

#### Page Tests (`frontend/src/pages/__tests__/`)

- **TaskDashboard.test.tsx** - Tests for task dashboard
  - Summary cards display
  - Task metrics calculation
  - Quick task creation
  - Authentication handling
  - Error states

### Backend Testing

#### API Endpoint Tests (`backend/tests/api/test_tasks.py`)

- **Task CRUD Operations**
  - Create tasks (success, validation errors)
  - Read tasks (by ID, filtering, pagination)
  - Update tasks (success, not found errors)
  - Delete tasks (success, not found errors)
  - Mark tasks complete

- **Authentication & Authorization**
  - Valid token access
  - Invalid token handling
  - Unauthorized access prevention

- **Filtering & Search**
  - Status filtering
  - Priority filtering
  - Category filtering
  - Text search
  - Combined filters
  - Pagination

- **Task Categories**
  - Category CRUD operations
  - Category assignment to tasks
  - Category ownership validation

- **Recurring Tasks**
  - Recurrence pattern creation
  - Recurrence updates
  - Lead time handling

#### Integration Tests (`backend/tests/integration/test_task_workflow.py`)

- **Complete Task Lifecycle**
  - Creation → In Progress → Completion workflow
  - Category assignment
  - Status transitions
  - Analytics updates

- **Recurring Task Workflow**
  - Recurring pattern setup
  - Task completion and next occurrence generation
  - Recurrence pattern updates

- **Bulk Operations**
  - Multiple task creation
  - Bulk updates
  - Bulk deletion

- **Search & Filtering Workflow**
  - Complex filtering scenarios
  - Search functionality
  - Combined filter operations

- **Error Handling**
  - Invalid data handling
  - Non-existent resource access
  - Authentication errors

- **Tenant Isolation**
  - Multi-tenant data separation
  - Access control validation

#### Performance Tests (`backend/tests/performance/test_task_performance.py`)

- **Load Testing**
  - Bulk task creation (100+ tasks)
  - Concurrent operations (read/write)
  - Database connection pool stress testing

- **Response Time Testing**
  - Task list performance with large datasets (1000+ tasks)
  - Complex filtering performance
  - Pagination performance

- **Scalability Testing**
  - Category creation and assignment
  - Concurrent user simulation
  - Database query optimization validation

### End-to-End Testing

#### E2E Tests (`frontend/tests/e2e/task-management.spec.ts`)

- **Complete User Workflows**
  - Login → Task Creation → Completion → Filtering
  - Task board (Kanban) interactions
  - Category management workflow
  - Search and filtering

- **UI Interactions**
  - Form submissions
  - Button clicks and navigation
  - Drag and drop (if implemented)
  - Modal interactions

- **Cross-Browser Testing**
  - Chrome, Firefox, Safari compatibility
  - Mobile responsiveness
  - Accessibility compliance

- **Error Scenarios**
  - Network errors
  - Form validation
  - API failures

## Test Infrastructure

### Frontend Setup

```bash
cd frontend
npm install
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- --coverage     # Coverage report
npm run test:e2e           # End-to-end tests
```

#### Key Dependencies
- Jest - Test runner
- React Testing Library - Component testing
- @testing-library/user-event - User interaction simulation
- Playwright - End-to-end testing

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
pytest                      # Run all tests
pytest -k "task"           # Run task-related tests only
pytest -v --cov           # Verbose output with coverage
pytest -m "performance"   # Run performance tests only
```

#### Key Dependencies
- pytest - Test runner
- pytest-asyncio - Async testing support
- FastAPI TestClient - API testing
- SQLAlchemy testing utilities

## CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/test-tasks.yml`)

The automated testing pipeline includes:

1. **Backend Tests**
   - Python 3.11 environment
   - PostgreSQL test database
   - Task-specific test execution
   - Coverage reporting

2. **Frontend Tests**
   - Node.js 18 environment
   - Component and hook testing
   - Coverage reporting

3. **Integration Tests**
   - Full-stack environment
   - API integration validation
   - Workflow testing

4. **E2E Tests**
   - Browser automation
   - Complete user journey testing
   - Cross-browser validation

5. **Performance Tests**
   - Load testing
   - Response time validation
   - Scalability assessment

### Coverage Targets

- **Backend**: >90% line coverage for task-related code
- **Frontend**: >80% line coverage for task components
- **Integration**: Complete workflow coverage
- **E2E**: Critical user journey coverage

## Test Data Management

### Mock Data (`frontend/src/__mocks__/taskMocks.ts`)

Provides comprehensive mock data for testing:
- Sample tasks with various states
- Task categories
- Recurrence patterns
- API responses (success and error)
- Helper functions for generating test data

### Test Fixtures (`backend/tests/conftest.py`)

Provides reusable test fixtures:
- Database sessions
- Authenticated users
- Test tenants
- Common test data

## Running Tests

### Local Development

```bash
# Backend tests
cd backend
pytest tests/test_task_crud.py -v
pytest tests/api/test_tasks.py -v
pytest tests/integration/test_task_workflow.py -v
pytest tests/performance/test_task_performance.py -v -m "performance"

# Frontend tests
cd frontend
npm test -- src/components/tasks/__tests__/
npm test -- src/hooks/__tests__/
npm test -- src/pages/__tests__/
npm run test:e2e -- tests/e2e/task-management.spec.ts
```

### Continuous Integration

Tests run automatically on:
- Push to main branch (for task-related files)
- Pull requests (for task-related files)
- Manual workflow dispatch

### Test Reports

- Coverage reports uploaded to Codecov
- E2E test artifacts stored for 30 days
- Performance metrics logged in CI output
- Test summaries in GitHub Actions

## Best Practices

### Writing Tests

1. **Descriptive Test Names** - Clearly describe what is being tested
2. **Arrange-Act-Assert** - Structure tests with clear setup, action, and verification
3. **Independent Tests** - Each test should be able to run independently
4. **Mock External Dependencies** - Use mocks for API calls and external services
5. **Test Error Conditions** - Include negative test cases
6. **Performance Considerations** - Include performance assertions where appropriate

### Maintaining Tests

1. **Keep Tests Updated** - Update tests when features change
2. **Regular Test Reviews** - Review test effectiveness periodically
3. **Flaky Test Handling** - Identify and fix unstable tests quickly
4. **Coverage Monitoring** - Maintain high test coverage
5. **Documentation** - Keep test documentation current

## Troubleshooting

### Common Issues

1. **Test Database Connection Errors**
   - Ensure PostgreSQL is running
   - Check connection parameters
   - Verify test database exists

2. **Frontend Test Failures**
   - Clear npm cache: `npm cache clean --force`
   - Reinstall dependencies: `rm -rf node_modules && npm install`
   - Check for outdated snapshots

3. **E2E Test Failures**
   - Ensure both frontend and backend are running
   - Check browser installation: `npx playwright install`
   - Verify test data setup

4. **Performance Test Variability**
   - Run on consistent hardware
   - Account for system load
   - Use relative performance metrics

### Debug Mode

```bash
# Backend debugging
pytest --pdb tests/test_file.py::test_function

# Frontend debugging
npm test -- --verbose tests/MyComponent.test.tsx

# E2E debugging with headed browser
npm run test:e2e -- --headed tests/e2e/test.spec.ts
```

## Contributing

When adding new task management features:

1. **Write Tests First** - Follow TDD practices
2. **Update Existing Tests** - Modify tests affected by changes
3. **Add Integration Tests** - Test feature interactions
4. **Include E2E Tests** - Test critical user paths
5. **Performance Testing** - Add performance tests for data-heavy features
6. **Update Documentation** - Keep this README current

## Future Enhancements

Planned testing improvements:

- Visual regression testing
- API contract testing
- Accessibility testing automation
- Mobile-specific E2E tests
- Load testing with realistic user patterns
- Chaos engineering tests
- Security testing automation

---

For questions or issues with the testing suite, please refer to the main project documentation or create an issue in the repository.