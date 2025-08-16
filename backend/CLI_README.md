# Recaller Backend CLI Tool

The Recaller Backend CLI Tool provides command-line interface for administrative tasks including user management, tenant operations, and system health checks.

## Installation

The CLI tool is located in the `backend/` directory and requires the backend dependencies to be installed:

```bash
cd backend
pip install -r requirements.txt
```

## Usage

The CLI tool is accessed through the `cli.py` script in the backend directory:

```bash
cd backend
python cli.py --help
```

## Commands

### User Management

#### Create User
Create a new user account:

```bash
python cli.py user create-user
```

Interactive prompts will ask for:
- Email address
- Password (hidden input)
- Full name
- Tenant ID (optional, defaults to 1)
- Superuser flag (optional)
- Active status (optional, defaults to active)

Or use command-line arguments:
```bash
python cli.py user create-user --email user@example.com --full-name "User Name" --tenant-id 1
```

#### Create Superuser
Create an administrator account:

```bash
python cli.py user create-superuser
```

#### List Users
Display all users:

```bash
python cli.py user list-users
```

Options:
- `--tenant-id <id>`: Filter by specific tenant
- `--active-only`: Show only active users
- `--limit <number>`: Limit number of results (default: 50)

#### Enable/Disable User
Enable or disable a user account:

```bash
python cli.py user enable-user --email user@example.com --tenant-id 1
python cli.py user disable-user --email user@example.com --tenant-id 1
```

#### Reset Password
Reset a user's password:

```bash
python cli.py user reset-password --email user@example.com --tenant-id 1
```

#### Delete User
Delete a user and all associated data:

```bash
python cli.py user delete-user --email user@example.com --tenant-id 1
```

Use `--force` flag to skip confirmation prompt:
```bash
python cli.py user delete-user --email user@example.com --tenant-id 1 --force
```

### Tenant Management

#### List Tenants
Display all tenants:

```bash
python cli.py tenant list-tenants
```

#### Create Tenant
Create a new tenant:

```bash
python cli.py tenant create-tenant --name "Tenant Name" --slug "tenant-slug"
```

### System Operations

#### Health Check
Check database connection and system health:

```bash
python cli.py health
```

## Features

- **Multi-tenant Support**: All user operations are tenant-aware
- **Security**: Passwords are automatically hashed before storage
- **Error Handling**: Comprehensive error messages and validation
- **Interactive Mode**: Prompts for required inputs when not provided
- **Confirmation Prompts**: Safety confirmations for destructive operations
- **Status Indicators**: Clear visual feedback with emojis and colors

## Examples

### Complete User Management Workflow

```bash
# Check system health
python cli.py health

# List available tenants
python cli.py tenant list-tenants

# Create a new user
python cli.py user create-user --email admin@company.com --full-name "Admin User" --is-superuser

# List all users
python cli.py user list-users

# Disable a user
python cli.py user disable-user --email admin@company.com --tenant-id 1

# Reset user password
python cli.py user reset-password --email admin@company.com --tenant-id 1

# Enable user back
python cli.py user enable-user --email admin@company.com --tenant-id 1
```

### Batch Operations

```bash
# Create multiple users (example with different tenants)
python cli.py user create-user --email user1@tenant1.com --full-name "User One" --tenant-id 1
python cli.py user create-user --email user2@tenant2.com --full-name "User Two" --tenant-id 2

# List users by tenant
python cli.py user list-users --tenant-id 1
python cli.py user list-users --tenant-id 2
```

## Development and Testing

For development, you can use the provided database initialization script to set up a test database:

```bash
python init_dev_db.py
```

This creates the necessary tables and a default tenant for testing CLI operations.

## Error Handling

The CLI tool provides clear error messages for common scenarios:

- **Duplicate emails**: Prevents creating users with existing email addresses
- **User not found**: Clear messages when trying to operate on non-existent users
- **Database errors**: Proper error handling for database connectivity issues
- **Validation errors**: Input validation with helpful error messages

## Security Considerations

- Passwords are never displayed in logs or output
- Password input is hidden during interactive prompts
- All database operations use proper transaction handling
- User deletion includes confirmation prompts for safety

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Ensure PostgreSQL is running (for production)
2. Check database configuration in environment variables
3. For development, the CLI falls back to SQLite automatically

### Permission Issues

If you see permission errors:

1. Ensure you have proper database access
2. Check file permissions on SQLite database files
3. Verify you're running from the correct directory

### Import Errors

If you see import errors:

1. Ensure you're in the `backend/` directory
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check Python path configuration

## Testing

The CLI tool includes comprehensive tests:

```bash
python -m pytest tests/test_cli_commands.py -v
```

Tests cover:
- User creation and management
- Error scenarios
- Database isolation
- Command validation