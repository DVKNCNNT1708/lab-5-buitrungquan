# Lab 05: FIT4110 Docker Compose Readiness

## Overview

This is a comprehensive implementation of **Lab 05: Docker Compose Readiness** for FIT4110 course. The project demonstrates a production-ready IoT ingestion system using Docker Compose with three services:
- **IoT API** (FastAPI) - Main API service for handling IoT readings
- **AI Service** (FastAPI) - Mock AI prediction service
- **PostgreSQL Database** - Data persistence layer

All services are orchestrated using Docker Compose, connected via an internal network, with proper health checks and dependency management.

## Features

### ✅ Core Requirements Met

1. **Docker Compose with 3 Services**
   - API service on port 8000
   - AI service on port 9000
   - PostgreSQL 16 Alpine database on port 5432

2. **Network & Storage**
   - Custom `team-internal` bridge network for service communication
   - Named volume `postgres_data` for database persistence

3. **Health Checks**
   - Database: `pg_isready` command
   - AI Service: HTTP `/health` endpoint
   - API Service: HTTP `/health` endpoint
   - All configured with proper intervals, timeouts, and retries

4. **API Endpoints**
   - `GET /health` - Service health status (public)
   - `POST /readings` - Create IoT reading (requires Bearer token)
   - Both endpoints fully implemented and tested

5. **AI Service Endpoints**
   - `GET /health` - Service health
   - `POST /predict` - Mock ML predictions with simple heuristics

6. **Security**
   - Non-root `appuser` in Dockerfile
   - Bearer token authentication (lab05-secret-token)
   - All sensitive config in `.env` file (not hardcoded)

7. **Service Dependencies**
   - API depends on both DB and AI service
   - Uses `depends_on` with `condition: service_healthy`
   - Ensures proper startup order

8. **Documentation**
   - [RUN_COMPOSE.md](RUN_COMPOSE.md) - Complete setup and testing guide
   - [checklists/readiness-checklist.md](checklists/readiness-checklist.md) - Deployment verification checklist
   - Makefile with convenient commands
   - This README with comprehensive overview

9. **Postman Testing**
   - Collection: `postman/collections/FIT4110_lab05_iot_compose.postman_collection.json`
   - Environment: `postman/environments/FIT4110_lab05_local.postman_environment.json`
   - Tests for health checks and reading endpoints
   - Authorization testing (valid token, missing token, invalid token)
   - Automation ready with Newman

## Project Structure

```
lab-5-buitrungquan/
├── README.md                                          # This file
├── RUN_COMPOSE.md                                     # Setup and execution guide
├── Dockerfile                                         # Multi-stage Python image
├── docker-compose.yml                                 # 3-service orchestration
├── .dockerignore                                      # Docker build ignores
├── .env.example                                       # Environment template
├── Makefile                                           # Build & run commands
├── requirements.txt                                   # Python dependencies
│
├── src/
│   ├── iot_app/
│   │   ├── __init__.py
│   │   └── main.py                                   # FastAPI IoT service
│   └── ai_service/
│       ├── __init__.py
│       └── main.py                                   # FastAPI AI mock service
│
├── contracts/
│   └── iot-ingestion.openapi.yaml                    # OpenAPI specification
│
├── postman/
│   ├── collections/
│   │   └── FIT4110_lab05_iot_compose.postman_collection.json
│   └── environments/
│       └── FIT4110_lab05_local.postman_environment.json
│
├── checklists/
│   └── readiness-checklist.md                        # 6-point verification checklist
│
└── reports/                                           # Newman test reports
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git (for cloning)
- curl (for manual testing)
- Optional: Postman or Newman for advanced testing

### Setup

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd lab-5-buitrungquan

# 2. Create environment file
cp .env.example .env

# 3. Start all services
docker compose up -d --build

# 4. Verify all services are healthy
docker compose ps                    # Check containers
curl http://localhost:8000/health    # API health
curl http://localhost:9000/health    # AI health
```

### Testing

```bash
# Option 1: Manual testing with curl
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer lab05-secret-token" \
  -d '{
    "device_id": "device-001",
    "metric": "temperature",
    "value": 25.5,
    "unit": "celsius"
  }'

# Option 2: Use Makefile
make test-compose              # Run Postman tests via Newman

# Option 3: Use Postman GUI
# Import environment and collection, then run
```

### Cleanup

```bash
make clean                     # Stop and remove everything
```

## API Documentation

### Service: iot-service (Port 8000)

#### GET /health
Health check endpoint - no authentication required.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "iot-service",
  "version": "1.0.0"
}
```

#### POST /readings
Create a new IoT reading. **Requires Bearer token.**

**Authentication:**
```
Authorization: Bearer lab05-secret-token
```

**Request Body:**
```json
{
  "device_id": "device-001",
  "metric": "temperature",
  "value": 25.5,
  "unit": "celsius"
}
```

**Success Response (200 OK):**
```json
{
  "reading_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "ai_result": {
    "label": "normal",
    "confidence": 0.98
  }
}
```

**Auth Error (401 Unauthorized):**
- Missing token: `{"detail": "Missing authorization token"}`
- Invalid token: `{"detail": "Invalid token"}`
- Malformed header: `{"detail": "Invalid authorization header"}`

### Service: ai-service (Port 9000)

#### GET /health
AI service health check.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "ai-service",
  "model": "mock-v1"
}
```

#### POST /predict
Make a prediction on sensor data (called internally by API).

**Request Body:**
```json
{
  "device_id": "device-001",
  "metric": "temperature",
  "value": 25.5,
  "unit": "celsius",
  "timestamp": "2026-06-09T12:00:00"
}
```

**Response (200 OK):**
```json
{
  "label": "normal",
  "confidence": 0.98
}
```

**Prediction Logic:**
- `value > 100`: anomaly (confidence 0.95)
- `50 < value <= 100`: warning (confidence 0.75)
- `value <= 50`: normal (confidence 0.98)

## Configuration

### Environment Variables (.env)

```env
# PostgreSQL
POSTGRES_USER=iotuser
POSTGRES_PASSWORD=iotpassword
POSTGRES_DB=iotdb
POSTGRES_HOST=db
POSTGRES_PORT=5432

# API
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_TOKEN=lab05-secret-token
AI_SERVICE_URL=http://ai-service:9000

# AI Service
AI_SERVICE_HOST=0.0.0.0
AI_SERVICE_PORT=9000

# Environment
ENVIRONMENT=docker
DEBUG=False
```

**Security Note:** Change `POSTGRES_PASSWORD` and `API_SECRET_TOKEN` in production. Never commit `.env` to version control.

## Docker Compose Details

### Services

**db** (PostgreSQL 16 Alpine)
- Port: 5432
- Volume: postgres_data
- Health Check: pg_isready
- Restart: unless-stopped

**ai-service** (FastAPI)
- Port: 9000
- Health Check: HTTP GET /health
- Depends on: db
- Restart: unless-stopped

**api** (FastAPI)
- Port: 8000
- Health Check: HTTP GET /health
- Depends on: db (healthy), ai-service (healthy)
- Restart: unless-stopped

### Network
- Name: team-internal
- Type: bridge
- Services communicate via DNS:
  - API → AI Service: `http://ai-service:9000`
  - API → Database: `db:5432`

### Volumes
- postgres_data: Local driver, stores PostgreSQL data

## Makefile Commands

```bash
make help          # Show all commands
make compose-up    # Build and start services
make compose-down  # Stop and remove services
make logs          # View logs from all services
make ps            # Show running containers
make test-compose  # Run Postman tests via Newman
make clean         # Complete cleanup (remove volumes)
```

## Testing & Verification

### Health Checks

```bash
# API Health
curl http://localhost:8000/health

# AI Service Health
curl http://localhost:9000/health

# Database Health
docker compose exec db pg_isready -U iotuser -d iotdb
```

### Authentication Tests

```bash
# Missing token (should fail)
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test","metric":"temp","value":25.5}'

# Invalid token (should fail)
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer wrong-token" \
  -d '{"device_id":"test","metric":"temp","value":25.5}'

# Valid token (should succeed)
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer lab05-secret-token" \
  -d '{"device_id":"test","metric":"temp","value":25.5}'
```

### Postman Tests

```bash
# Run Newman tests (requires docker)
make test-compose

# Reports generated in reports/ directory:
# - newman-report.html
# - newman-report.json
```

See [RUN_COMPOSE.md](RUN_COMPOSE.md) for detailed testing instructions.

## Readiness Checklist

Before considering the system production-ready, verify all 6 checkpoint categories:

1. ✅ **Database Ready** - PostgreSQL running with health checks
2. ✅ **AI Service Ready** - /health and /predict endpoints working
3. ✅ **API Service Ready** - /health and /readings endpoints working
4. ✅ **Authorization Token Validation** - Auth tests passing
5. ✅ **Port Configuration** - All ports accessible without conflicts
6. ✅ **Internal Network Configuration** - Services communicating via team-internal network

See [checklists/readiness-checklist.md](checklists/readiness-checklist.md) for complete verification procedures.

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs -f

# Rebuild without cache
docker compose up -d --build --no-cache

# Full reset
docker compose down -v
docker system prune -a
docker compose up -d --build
```

### Port Conflicts

```bash
# Find what's using the port
lsof -i :8000
lsof -i :9000
lsof -i :5432

# Kill the process if needed
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
# Check if running
docker compose ps ai-service

# Test from API container
docker compose exec api curl http://ai-service:9000/health
```

## Lab 04 Compatibility

This Lab 05 implementation is built on top of Lab 04 FastAPI foundations:
- Reuses core API logic and patterns
- Maintains compatibility with existing data models
- Extends with Docker Compose orchestration
- Adds AI service integration

## Production Considerations

⚠️ **Important Security Notes:**

1. Change default credentials in `.env`
2. Use environment-specific configurations
3. Implement proper authentication (OAuth2, JWT)
4. Use secrets management (Docker Secrets, HashiCorp Vault)
5. Set up logging and monitoring
6. Configure resource limits
7. Use health checks in production

## Dependencies

### Python Packages
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- requests==2.31.0
- psycopg2-binary==2.9.9
- python-dotenv==1.0.0

### System
- Docker
- Docker Compose
- PostgreSQL 16 (Alpine)
- Python 3.12

## License

Lab project for FIT4110 course.

## Support

For detailed instructions on:
- **Setup & Execution**: See [RUN_COMPOSE.md](RUN_COMPOSE.md)
- **Verification**: See [checklists/readiness-checklist.md](checklists/readiness-checklist.md)
- **API Details**: See [contracts/iot-ingestion.openapi.yaml](contracts/iot-ingestion.openapi.yaml)

## Authors

FIT4110 - Smart Campus IoT Lab

---

**Status**: ✅ Complete Lab 05 Implementation

Last Updated: June 2026
