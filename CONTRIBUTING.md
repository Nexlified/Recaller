# Contributing to Recaller

Thank you for your interest in contributing to Recaller! We welcome contributions from the community and are excited to see what you'll build.

## 🤝 How to Contribute

### 1. Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/recaller.git
   cd recaller
   ```

### 2. Set Up Development Environment

Follow the setup instructions in the [README.md](README.md):

```bash
# Using Docker Compose (recommended)
docker-compose up --build

# Or manual setup
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### 3. Create a Branch

Create a new branch for your feature or fix:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 4. Make Your Changes

- Write clean, well-documented code
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

### 5. Test Your Changes

```bash
# Backend tests
cd backend && pytest

# Frontend tests  
cd frontend && npm test

# Integration tests
npm run test:playwright
```

### 6. Submit a Pull Request

1. Push your changes to your fork
2. Create a pull request against the main branch
3. Provide a clear description of your changes
4. Link any related issues

## 📋 Contribution Guidelines

### Code Style

- **Backend (Python)**: Follow PEP 8, use type hints
- **Frontend (TypeScript)**: Use ESLint configuration, prefer functional components
- **Documentation**: Use clear, concise language with examples

### Commit Messages

Use conventional commit format:
```
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add unit tests for user service
```

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add a clear description of changes
4. Request review from maintainers
5. Address feedback promptly

## 🐛 Bug Reports

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, versions)
- Relevant logs or screenshots

Use our bug report template in GitHub Issues.

## 💡 Feature Requests

For new features:

- Check existing issues first
- Describe the problem you're solving
- Explain your proposed solution
- Consider implementation complexity
- Discuss with maintainers before starting large features

## 🏗️ Development Guidelines

### Architecture Principles

- **Privacy First**: No user data sent to third-party services
- **Multi-tenant**: Support multiple organizations/users
- **Self-hosted**: Easy deployment and maintenance
- **Open Source**: Community-driven development

### Code Quality

- Write tests for new features
- Maintain test coverage above 80%
- Use type safety (TypeScript, Python type hints)
- Document complex business logic
- Handle errors gracefully

### Security

- Validate all inputs
- Use parameterized queries
- Implement proper authentication/authorization
- Follow OWASP guidelines
- Report security issues privately

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run specific test categories
pytest -m auth
pytest -m integration

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

### Frontend Testing

```bash
cd frontend

# Unit tests
npm test

# E2E tests
npm run test:playwright

# Generate screenshots
npm run screenshots:generate
```

### Test Requirements

- Unit tests for new functions/components
- Integration tests for API endpoints
- E2E tests for critical user flows
- Test edge cases and error scenarios

## 📚 Documentation

### What to Document

- New API endpoints
- Configuration changes
- Setup procedures
- Architecture decisions
- Breaking changes

### Documentation Standards

- Use clear, concise language
- Include code examples
- Provide context and rationale
- Keep it up-to-date

## 🔧 Development Tools

### Recommended Setup

- **IDE**: VS Code with recommended extensions
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Node**: 18+ LTS
- **Python**: 3.10+

### Useful Commands

```bash
# Start development environment
docker-compose up --build

# Backend development
cd backend && uvicorn app.main:app --reload

# Frontend development  
cd frontend && npm run dev

# Database migrations
cd backend && alembic upgrade head

# View logs
docker-compose logs -f
```

## 🌍 Community

### Getting Help

- 📖 Read the documentation first
- 🔍 Search existing issues
- 💬 Join our community chat (coming soon)
- ❓ Ask questions in GitHub Discussions

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful, constructive, and helpful in all interactions.

## 📄 License

By contributing to Recaller, you agree that your contributions will be licensed under the same license as the project (AGPLv3).

---

Thank you for contributing to Recaller! 🎉

*For more information, see our [README.md](README.md) or contact the maintainers.*