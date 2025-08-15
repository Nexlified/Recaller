# GitHub Issue Templates

This directory contains issue templates for the Recaller project to help users report bugs and request features in a structured way.

## Available Templates

### 🐛 Frontend Bug Report (`01-frontend-bug.yml`)
Use this template when reporting bugs related to the frontend (React/Next.js/TypeScript).

**When to use:**
- UI/UX issues
- Browser compatibility problems
- JavaScript errors in console
- Responsive design issues
- Form validation problems
- Navigation issues

**Key fields:**
- Browser and version information
- Screen resolution and device type
- Console errors
- Screenshots

### ⚙️ Backend Bug Report (`02-backend-bug.yml`)
Use this template when reporting bugs related to the backend (FastAPI/Python/Database).

**When to use:**
- API endpoint errors
- Database issues
- Authentication/authorization problems
- Server performance issues
- Data validation errors
- Background task failures

**Key fields:**
- API endpoint and HTTP method
- Request/response payload
- Server logs
- Database errors
- Environment configuration

### 🐞 Bug Report (`03-bug-report.yml`)
Use this general template when you're not sure if the issue is frontend or backend related, or when it affects multiple components.

**When to use:**
- Cross-component issues
- General application problems
- When unsure about the root cause
- Integration issues
- Performance problems affecting the entire app

**Key fields:**
- Affected area of the application
- User type and deployment method
- General environment information
- Frequency of the issue

### ✨ Feature Request (`04-feature-request.yml`)
Use this template to suggest new features or enhancements.

**When to use:**
- Proposing new functionality
- Suggesting improvements to existing features
- Requesting integrations
- Performance enhancements
- UX improvements

**Key fields:**
- Problem description and proposed solution
- User stories and use cases
- Implementation ideas
- Priority and impact assessment

## Template Features

All templates include:

- **Prerequisites**: Checkboxes to ensure users have searched for duplicates and read contributing guidelines
- **Structured Information**: Organized fields to collect relevant technical details
- **Severity/Priority Levels**: To help with issue triage
- **Environment Details**: To reproduce issues accurately
- **Additional Context**: For any extra information

## Using the Templates

1. Go to the [Issues page](https://github.com/Nexlified/Recaller/issues)
2. Click "New Issue"
3. Select the appropriate template
4. Fill out the form completely
5. Submit the issue

## Configuration

The `config.yml` file provides:
- Links to community resources (Discussions, Documentation)
- Option to create blank issues for edge cases
- Quick access to contributing guidelines

## Template Guidelines

When creating or modifying templates:

1. **Keep forms concise** but comprehensive
2. **Include validation** for required fields
3. **Provide clear descriptions** for each field
4. **Use dropdown menus** for standardized values
5. **Include examples** in placeholders
6. **Align with project tech stack** (FastAPI, Next.js, PostgreSQL, Docker)

## Contributing

If you'd like to suggest improvements to these templates, please:

1. Create a feature request using the feature request template
2. Describe your proposed changes
3. Explain the benefits
4. Consider backward compatibility

These templates are designed to improve issue quality and help maintainers provide better support to the community.