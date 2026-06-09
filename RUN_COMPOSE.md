# Lab 05: Docker Compose Readiness - Run Guide

## Overview
This lab demonstrates a complete Docker Compose setup for an IoT ingestion system with API, AI service, and PostgreSQL database.

## Prerequisites
- Docker and Docker Compose installed
- Git
- cURL (for testing)
- Optional: Postman/Newman for API testing

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd lab-5-buitrungquan
```

### 2. Create Environment File
```bash
cp .env.example .env
```

### 3. Build and Start Services
```bash
docker compose up -d --build
```

### 4. Verify Services are Running
```bash
docker compose ps
```

Expected output should show 3 containers:
- `iot-db` (postgres:16-alpine)
- `iot-ai-service` (FastAPI)
- `iot-api` (FastAPI)

### 5. Check Health Endpoints

#### API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "iot-service",
  "version": "1.0.0"
}
```

#### AI Service Health
```bash
curl http://localhost:9000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "ai-service",
  "model": "mock-v1"
}
```

#### Database Health
```bash
docker compose exec db pg_isready -U iotuser -d iotdb
```

Expected output: `accepting connections`

### 6. Test API Endpoints

#### Test Health Check (No Auth Required)
```bash
curl -X GET http://localhost:8000/health
```

#### Test Health Check with Token (Should Still Work)
```bash
curl -X GET http://localhost:8000/health \
  -H "Authorization: Bearer lab05-secret-token"
```

#### Test Missing Token (Should Return 401)
```bash
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device-001",
    "metric": "temperature",
    "value": 25.5,
    "unit": "celsius"
  }'
```

Expected response: `401 Unauthorized`

#### Test with Valid Token (Should Return 200/201)
```bash
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer lab05-secret-token" \
  -d '{
    "device_id": "device-001",
    "metric": "temperature",
    "value": 25.5,
    "unit": "celsius"
  }'
```

Expected response:
```json
{
  "reading_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "success",
  "ai_result": {
    "label": "normal",
    "confidence": 0.98
  }
}
```

#### Test with Invalid Token (Should Return 401)
```bash
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid-token" \
  -d '{
    "device_id": "device-001",
    "metric": "temperature",
    "value": 25.5,
    "unit": "celsius"
  }'
```

Expected response: `401 Unauthorized`

### 7. View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f ai-service
docker compose logs -f db
```

### 8. Run Postman Tests

#### Using Newman (CLI)
```bash
make test-compose
```

This will:
- Run all tests in the Postman collection
- Generate HTML report in `reports/newman-report.html`
- Generate JSON report in `reports/newman-report.json`

#### Using Postman Desktop App
1. Import collection: `postman/collections/FIT4110_lab05_iot_compose.postman_collection.json`
2. Import environment: `postman/environments/FIT4110_lab05_local.postman_environment.json`
3. Select the imported environment
4. Click the collection runner button
5. Run the collection

### 9. Check Readiness Checklist
See [checklists/readiness-checklist.md](checklists/readiness-checklist.md) for verification steps.

## Makefile Commands

```bash
# Start services
make compose-up

# Stop services
make compose-down

# View logs
make logs

# Show running containers
make ps

# Run tests
make test-compose

# Clean up (remove containers and volumes)
make clean
```

## Network Configuration

All services are connected via `team-internal` network:
- **API** (iot-api): http://localhost:8000
- **AI Service** (iot-ai-service): http://localhost:9000
- **Database** (iot-db): localhost:5432

From within Docker network:
- API can reach AI Service at: `http://ai-service:9000`
- Both services can reach Database at: `db:5432`

## Environment Variables

Key variables from `.env`:
- `POSTGRES_USER`: Database user (default: iotuser)
- `POSTGRES_PASSWORD`: Database password
- `API_SECRET_TOKEN`: Bearer token for API (default: lab05-secret-token)
- `AI_SERVICE_URL`: URL to AI service (default: http://ai-service:9000)

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker compose logs -f <service-name>

# Rebuild without cache
docker compose up -d --build --no-cache

# Reset everything
docker compose down -v
docker system prune -a
docker compose up -d --build
```

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :9000
lsof -i :5432

# Or kill the process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check database health
docker compose exec db pg_isready -U iotuser -d iotdb

# Connect to database
docker compose exec db psql -U iotuser -d iotdb
```

### AI Service Unreachable
```bash
# Check if service is running
docker compose ps ai-service

# Test connection from API
docker compose exec api curl http://ai-service:9000/health
```

## Security Notes
- The token `lab05-secret-token` is for **development/testing only**
- Never commit `.env` with real credentials
- Use environment variables for all sensitive data
- In production, implement proper authentication (OAuth2, JWT, etc.)

## Additional Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Postman Documentation](https://learning.postman.com/)
