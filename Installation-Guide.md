# Installation Guide

This guide provides step-by-step instructions for installing and setting up Recaller in various environments, from local development to production deployment.

## 🚀 Quick Start (Docker Compose)

The fastest way to get Recaller running is with Docker Compose:

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nexlified/Recaller.git
   cd Recaller
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Wait for services to initialize** (first run takes 2-3 minutes)

4. **Access the application:**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Task Monitor (Flower)**: http://localhost:5555

5. **Create your first user account** through the frontend registration flow

That's it! Recaller is now running with all services.

## 🛠️ Manual Installation

For development or custom deployment scenarios:

### Backend Setup (FastAPI)

#### Prerequisites
- Python 3.10 or higher
- PostgreSQL 13+
- Redis 6+

#### Installation Steps

1. **Clone and navigate to backend:**
   ```bash
   git clone https://github.com/Nexlified/Recaller.git
   cd Recaller/backend
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis configurations
   ```

5. **Set up database:**
   ```bash
   # Create PostgreSQL database
   createdb recaller
   
   # Run migrations
   alembic upgrade head
   ```

6. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start background workers (separate terminals):**
   ```bash
   # Celery worker
   celery -A app.services.background_tasks:celery_app worker --loglevel=info
   
   # Celery beat scheduler
   celery -A app.services.background_tasks:celery_app beat --loglevel=info
   
   # Optional: Flower monitoring
   celery -A app.services.background_tasks:celery_app flower
   ```

### Frontend Setup (React)

#### Prerequisites
- Node.js 18+ and npm/yarn
- Backend running on http://localhost:8000

#### Installation Steps

1. **Navigate to frontend directory:**
   ```bash
   cd Recaller/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

4. **Start development server:**
   ```bash
   npm start
   # or
   yarn start
   ```

5. **Access frontend at** http://localhost:3000

## 🗄️ Database Setup

### PostgreSQL Configuration

#### Using Docker:
```bash
docker run --name recaller-postgres \
  -e POSTGRES_USER=recaller \
  -e POSTGRES_PASSWORD=recaller \
  -e POSTGRES_DB=recaller \
  -p 5432:5432 \
  -d postgres:15
```

#### Manual Installation:
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create user and database
sudo -u postgres psql
CREATE USER recaller WITH PASSWORD 'recaller';
CREATE DATABASE recaller OWNER recaller;
GRANT ALL PRIVILEGES ON DATABASE recaller TO recaller;
\q
```

### Redis Configuration

#### Using Docker:
```bash
docker run --name recaller-redis \
  -p 6379:6379 \
  -d redis:7-alpine
```

#### Manual Installation:
```bash
# Install Redis (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Database Migrations

After setting up PostgreSQL, run the migrations:

```bash
cd backend
alembic upgrade head
```

To create a new migration after model changes:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## ⚙️ Environment Configuration

### Backend Environment Variables (.env)

```bash
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=recaller
POSTGRES_PASSWORD=recaller
POSTGRES_DB=recaller

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security Settings
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# API Configuration
PROJECT_NAME=Recaller
VERSION=1.0.0
API_V1_STR=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
SMTP_FROM_EMAIL=noreply@recaller.com

# Development Settings
DEBUG=true
ENVIRONMENT=development
```

### Frontend Environment Variables (.env)

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Application Settings
REACT_APP_NAME=Recaller
REACT_APP_VERSION=1.0.0

# Development Settings
GENERATE_SOURCEMAP=true
```

## 🐳 Production Deployment

### Docker Production Setup

1. **Create production docker-compose file:**
   ```yaml
   # docker-compose.prod.yml
   version: '3.8'
   
   services:
     backend:
       build: 
         context: ./backend
         dockerfile: Dockerfile.prod
       environment:
         - DATABASE_URL=postgresql://user:pass@db:5432/recaller
         - REDIS_URL=redis://redis:6379/0
         - SECRET_KEY=${SECRET_KEY}
       depends_on:
         - db
         - redis
   
     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile.prod
       ports:
         - "80:80"
       depends_on:
         - backend
   
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: recaller
         POSTGRES_USER: ${POSTGRES_USER}
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
     redis:
       image: redis:7-alpine
       volumes:
         - redis_data:/data
   
     celery_worker:
       build: ./backend
       command: celery -A app.services.background_tasks:celery_app worker --loglevel=info
       depends_on:
         - db
         - redis
   
     celery_beat:
       build: ./backend
       command: celery -A app.services.background_tasks:celery_app beat --loglevel=info
       depends_on:
         - db
         - redis
   
   volumes:
     postgres_data:
     redis_data:
   ```

2. **Deploy with production settings:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Kubernetes Deployment

Example Kubernetes deployment files:

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recaller-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: recaller-backend
  template:
    metadata:
      labels:
        app: recaller-backend
    spec:
      containers:
      - name: backend
        image: recaller/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: recaller-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/recaller
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket support (if needed)
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🔒 Security Configuration

### SSL/TLS Setup

1. **Obtain SSL certificate** (Let's Encrypt recommended):
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

2. **Update Nginx configuration** for HTTPS:
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       # ... rest of configuration
   }
   ```

### Firewall Configuration

```bash
# Allow HTTP, HTTPS, and SSH
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Block direct access to database and Redis
sudo ufw deny 5432
sudo ufw deny 6379
```

### Backup Strategy

```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/backups/recaller"
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
pg_dump -h localhost -U recaller recaller > "$BACKUP_DIR/recaller_$DATE.sql"

# Compress and rotate backups
gzip "$BACKUP_DIR/recaller_$DATE.sql"
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete
```

## ✅ Health Checks

### Backend Health Check

```bash
curl http://localhost:8000/health
```

### Database Connection Check

```bash
# From backend directory
python -c "
from app.db.session import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection: FAILED - {e}')
finally:
    db.close()
"
```

### Redis Connection Check

```bash
redis-cli ping
```

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

2. **Database connection issues:**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   # Restart if needed
   sudo systemctl restart postgresql
   ```

3. **Frontend not connecting to backend:**
   - Verify REACT_APP_API_URL in frontend/.env
   - Check CORS settings in backend configuration
   - Ensure backend is running and accessible

4. **Celery workers not processing tasks:**
   ```bash
   # Check Redis connection
   redis-cli ping
   # Restart Celery workers
   pkill -f "celery worker"
   celery -A app.services.background_tasks:celery_app worker --loglevel=info
   ```

### Log Locations

- **Backend logs**: Check terminal output or configure logging to files
- **PostgreSQL logs**: `/var/log/postgresql/postgresql-*.log`
- **Nginx logs**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- **Docker logs**: `docker-compose logs <service-name>`

## 📚 Next Steps

After successful installation:

1. [Quick Start Tutorial](Quick-Start-Tutorial) - Learn basic operations
2. [System Architecture](System-Architecture) - Understand the system design
3. [Financial Management System](Financial-Management-System) - Set up financial tracking
4. [Contributing Guidelines](Contributing-Guidelines) - Contribute to the project

---

*For additional help, check our [GitHub Issues](https://github.com/Nexlified/Recaller/issues) or [Discussions](https://github.com/Nexlified/Recaller/discussions)*