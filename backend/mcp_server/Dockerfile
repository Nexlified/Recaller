FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY ../requirements.txt ./backend-requirements.txt

# Install backend dependencies first (shared dependencies)
RUN pip install --no-cache-dir -r backend-requirements.txt

# Install MCP server specific dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for models and logs
RUN mkdir -p /app/models /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/v1/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8001"]