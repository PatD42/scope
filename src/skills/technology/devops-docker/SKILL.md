---
name: devops-docker
description: Docker containerization best practices. Use when story requires Docker containers, Dockerfiles, multi-stage builds, docker-compose, container optimization, networking, volumes, or deployment patterns.
---

# DevOps Docker

Docker containerization patterns and best practices for building, optimizing, and deploying containers.

## Dockerfile Best Practices

```dockerfile
# Use specific version, not :latest
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "main.py"]
```

## Multi-Stage Builds

```dockerfile
# Build stage
FROM python:3.11 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Update PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["python", "main.py"]
```

## Layer Optimization

```dockerfile
# ❌ Bad - creates large layers
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y make

# ✅ Good - single layer, cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        make \
    && rm -rf /var/lib/apt/lists/*
```

## .dockerignore

```
# .dockerignore
.git
.env
*.pyc
__pycache__
.pytest_cache
node_modules
*.log
.DS_Store
.vscode
.idea
```

## Docker Compose

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./logs:/app/logs
    networks:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    networks:
      - backend
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

networks:
  backend:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

## Networking

```bash
# Create custom network
docker network create myapp-network

# Run containers on network
docker run --network myapp-network --name app ...
docker run --network myapp-network --name db ...

# Containers can reach each other by name
# app can connect to: postgresql://db:5432
```

## Volumes

```bash
# Named volume (managed by Docker)
docker volume create mydata
docker run -v mydata:/data myimage

# Bind mount (host directory)
docker run -v $(pwd)/data:/data myimage

# Read-only mount
docker run -v $(pwd)/config:/config:ro myimage
```

## Environment Variables

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - NODE_ENV=production
      - API_KEY=${API_KEY}  # From host environment
    env_file:
      - .env.production
```

## Security Hardening

```dockerfile
# Use non-root user
RUN useradd -r -u 1000 appuser
USER appuser

# Use minimal base image
FROM alpine:3.18

# Don't expose sensitive ports
EXPOSE 8000  # Application port
# Don't expose: 5432 (DB), 6379 (Redis)

# Read-only filesystem
docker run --read-only --tmpfs /tmp myimage

# Drop capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myimage

# Resource limits
docker run --memory=512m --cpus=0.5 myimage
```

## Health Checks

```dockerfile
# Application health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
    CMD curl -f http://localhost:8000/health || exit 1

# Database health check (docker-compose)
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U user"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## Build Arguments

```dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

ARG APP_VERSION=latest
LABEL version=${APP_VERSION}

# Build
docker build --build-arg PYTHON_VERSION=3.12 --build-arg APP_VERSION=1.0.0 .
```

## Image Optimization

```dockerfile
# Use alpine for smaller images
FROM python:3.11-alpine  # ~50MB vs 120MB for slim

# Multi-stage build (only copy runtime deps)
FROM builder AS runtime
COPY --from=builder /app/dist /app

# Combine RUN commands
RUN apk add --no-cache gcc && \
    pip install -r requirements.txt && \
    apk del gcc

# Use .dockerignore
# Reduces build context size
```

## Container Patterns

### Init Container

```yaml
services:
  init:
    image: myapp:latest
    command: python manage.py migrate
    depends_on:
      db:
        condition: service_healthy

  app:
    image: myapp:latest
    depends_on:
      init:
        condition: service_completed_successfully
```

### Sidecar Container

```yaml
services:
  app:
    image: myapp:latest
    volumes:
      - logs:/var/log

  log-shipper:
    image: fluent/fluentd:latest
    volumes:
      - logs:/var/log:ro
    depends_on:
      - app
```

## Debugging

```bash
# View logs
docker logs -f container_name

# Execute command in running container
docker exec -it container_name bash

# Inspect container
docker inspect container_name

# View resource usage
docker stats

# Copy files from container
docker cp container_name:/app/logs ./logs
```

## CI/CD Integration

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Run tests
        run: docker run myapp:${{ github.sha }} pytest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myapp:${{ github.sha }}
```

## Best Practices

1. **Use specific versions**: Not :latest
2. **Minimize layers**: Combine RUN commands
3. **Order layers by change frequency**: Deps before code
4. **Use .dockerignore**: Reduce build context
5. **Run as non-root**: Security best practice
6. **Health checks**: Enable restart policies
7. **Resource limits**: Set memory/CPU limits
8. **Multi-stage builds**: Separate build and runtime
9. **Cache dependencies**: Copy requirements before code
10. **Tag properly**: Use semantic versioning
