# Database Migration Strategies for Recaller Backend

This document outlines different approaches to running database migrations in the Recaller backend Docker container.

## Approach 1: Runtime Migrations (Recommended)

**File**: `Dockerfile` (default)

This approach runs migrations when the container starts, not during build. This is the recommended approach for most use cases.

### How it works:
1. Container starts with `docker-entrypoint.sh`
2. Script waits for database to be ready using `pg_isready`
3. Runs `alembic upgrade head`
4. Starts the FastAPI application

### Advantages:
- ✅ Database doesn't need to be available during build
- ✅ Works well with Docker Compose and orchestration tools
- ✅ Handles database connectivity issues gracefully
- ✅ Migrations run in the same environment as the application

### Usage:
```bash
# Standard docker-compose usage
docker-compose up --build

# Or directly with Docker
docker build -t recaller-backend ./backend
docker run -e POSTGRES_SERVER=db -e POSTGRES_USER=recaller -e POSTGRES_PASSWORD=recaller -e POSTGRES_DB=recaller recaller-backend
```

## Approach 2: Build-time Migrations (Advanced)

**File**: `Dockerfile.build-migrations`

This approach runs migrations during the container build process.

### How it works:
1. Database connection parameters provided as build arguments
2. Build process waits for database and runs migrations
3. Final container includes migrated state

### Advantages:
- ✅ Migrations are "baked into" the container image
- ✅ Faster container startup time
- ✅ Immutable deployment artifacts

### Disadvantages:
- ❌ Requires database to be available during build
- ❌ More complex build process
- ❌ Harder to handle migration failures
- ❌ Not suitable for CI/CD pipelines without accessible databases

### Usage:
```bash
# Using docker-compose override
docker-compose -f docker-compose.yml -f docker-compose.build-migrations.yml up --build

# Or directly with Docker build args
docker build -f Dockerfile.build-migrations \
  --build-arg POSTGRES_SERVER=your-db-host \
  --build-arg POSTGRES_USER=recaller \
  --build-arg POSTGRES_PASSWORD=recaller \
  --build-arg POSTGRES_DB=recaller \
  -t recaller-backend ./backend
```

## Approach 3: Manual Migrations

**File**: `run-migrations.sh`

Run migrations manually outside of the container build/start process.

### Usage:
```bash
# From the backend directory
./run-migrations.sh

# Or with Docker Compose
docker-compose exec backend ./run-migrations.sh

# Or create a one-off container
docker-compose run --rm backend alembic upgrade head
```

## Production Recommendations

### For Development:
Use **Approach 1** (Runtime Migrations) with docker-compose for simplicity.

### For Production:
Consider these strategies:

1. **Blue-Green Deployments**: Run migrations in a separate job before deploying new containers
2. **Init Containers**: Use Kubernetes init containers to run migrations before app containers start  
3. **Migration Jobs**: Run migrations as separate container jobs in your orchestration platform
4. **Database CI/CD**: Include migration testing in your CI/CD pipeline

### Example Production Migration Job:
```bash
# Run as a separate job before deploying app containers
docker run --rm \
  -e POSTGRES_SERVER=prod-db-host \
  -e POSTGRES_USER=recaller \
  -e POSTGRES_PASSWORD=$DB_PASSWORD \
  -e POSTGRES_DB=recaller \
  recaller-backend:latest \
  alembic upgrade head
```

## Environment Variables

All approaches use these environment variables for database connectivity:

```bash
POSTGRES_SERVER=localhost     # Database host
POSTGRES_USER=recaller       # Database user
POSTGRES_PASSWORD=recaller   # Database password
POSTGRES_DB=recaller        # Database name
POSTGRES_PORT=5432          # Database port (optional, defaults to 5432)
```

## Troubleshooting

### Migration Failures
- Check database connectivity with `pg_isready`
- Verify environment variables are set correctly
- Check Alembic configuration in `alembic.ini`
- Review migration files for syntax errors

### Container Won't Start
- Check logs with `docker-compose logs backend`
- Verify database is healthy with `docker-compose ps`
- Test database connection manually

### Permission Issues
- Ensure `docker-entrypoint.sh` is executable
- Check file ownership in the container
- Verify database user has necessary permissions

## Files Overview

- `Dockerfile` - Default runtime migrations approach
- `Dockerfile.build-migrations` - Build-time migrations approach  
- `Dockerfile.prod` - Production-ready template
- `docker-entrypoint.sh` - Entrypoint script for runtime migrations
- `run-migrations.sh` - Manual migration script
- `docker-compose.build-migrations.yml` - Compose override for build-time migrations
