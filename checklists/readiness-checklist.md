# Lab 05 FIT4110: Docker Compose Readiness Checklist

## Deployment Readiness Verification

Use this checklist to verify that all services are properly configured and operational before deployment.

---

## ✓ 1. Database Ready

- [ ] PostgreSQL container is running
  ```bash
  docker compose ps db
  ```
  Expected: Status should show "Up" and port 5432 mapped

- [ ] Database health check passes
  ```bash
  docker compose exec db pg_isready -U iotuser -d iotdb
  ```
  Expected: Output should be "accepting connections"

- [ ] Database is accessible from API container
  ```bash
  docker compose exec api pg_isready -U iotuser -h db -d iotdb
  ```
  Expected: Output should be "accepting connections"

- [ ] Data volume is created and mounted
  ```bash
  docker volume ls | grep postgres_data
  ```
  Expected: postgres_data volume should be listed

---

## ✓ 2. AI Service Ready

- [ ] AI Service container is running
  ```bash
  docker compose ps ai-service
  ```
  Expected: Status should show "Up" and port 9000 mapped

- [ ] AI Service health endpoint returns 200
  ```bash
  curl -X GET http://localhost:9000/health
  ```
  Expected: 
  ```json
  {
    "status": "ok",
    "service": "ai-service",
    "model": "mock-v1"
  }
  ```

- [ ] AI Service /predict endpoint works
  ```bash
  curl -X POST http://localhost:9000/predict \
    -H "Content-Type: application/json" \
    -d '{"device_id":"test","metric":"temp","value":25.5,"unit":"C"}'
  ```
  Expected: 
  ```json
  {
    "label": "normal",
    "confidence": 0.98
  }
  ```

- [ ] AI Service is accessible from API container (internal network)
  ```bash
  docker compose exec api curl http://ai-service:9000/health
  ```
  Expected: Should return 200 with health response

---

## ✓ 3. API Service Ready

- [ ] API container is running
  ```bash
  docker compose ps api
  ```
  Expected: Status should show "Up" and port 8000 mapped

- [ ] API health endpoint returns 200 (no auth required)
  ```bash
  curl -X GET http://localhost:8000/health
  ```
  Expected:
  ```json
  {
    "status": "ok",
    "service": "iot-service",
    "version": "1.0.0"
  }
  ```

- [ ] API /readings endpoint requires authentication
  ```bash
  curl -X POST http://localhost:8000/readings \
    -H "Content-Type: application/json" \
    -d '{"device_id":"test","metric":"temp","value":25.5,"unit":"C"}'
  ```
  Expected: Status code 401 with message "Missing authorization token"

- [ ] API /readings works with valid token
  ```bash
  curl -X POST http://localhost:8000/readings \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer lab05-secret-token" \
    -d '{"device_id":"test","metric":"temp","value":25.5,"unit":"C"}'
  ```
  Expected: Status code 200/201 with reading_id and ai_result

---

## ✓ 4. Authorization Token Validation

- [ ] Correct token works (lab05-secret-token)
  ```bash
  curl -X POST http://localhost:8000/readings \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer lab05-secret-token" \
    -d '{"device_id":"device-001","metric":"temperature","value":25.5,"unit":"celsius"}'
  ```
  Expected: Status 200 with success response

- [ ] Missing Authorization header returns 401
  ```bash
  curl -X POST http://localhost:8000/readings \
    -H "Content-Type: application/json" \
    -d '{"device_id":"device-001","metric":"temperature","value":25.5,"unit":"celsius"}'
  ```
  Expected: Status 401 with "Missing authorization token"

- [ ] Invalid token returns 401
  ```bash
  curl -X POST http://localhost:8000/readings \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer wrong-token" \
    -d '{"device_id":"device-001","metric":"temperature","value":25.5,"unit":"celsius"}'
  ```
  Expected: Status 401 with "Invalid token"

- [ ] Malformed Authorization header returns 401
  ```bash
  curl -X POST http://localhost:8000/readings \
    -H "Content-Type: application/json" \
    -H "Authorization: InvalidFormat" \
    -d '{"device_id":"device-001","metric":"temperature","value":25.5,"unit":"celsius"}'
  ```
  Expected: Status 401 with "Invalid authorization header"

---

## ✓ 5. Port Configuration Verification

- [ ] API is accessible on port 8000
  ```bash
  netstat -tulpn | grep 8000
  # or
  lsof -i :8000
  ```
  Expected: Port 8000 should be listening

- [ ] AI Service is accessible on port 9000
  ```bash
  netstat -tulpn | grep 9000
  # or
  lsof -i :9000
  ```
  Expected: Port 9000 should be listening

- [ ] Database is accessible on port 5432
  ```bash
  netstat -tulpn | grep 5432
  # or
  lsof -i :5432
  ```
  Expected: Port 5432 should be listening

- [ ] No port conflicts
  ```bash
  docker compose ps
  ```
  Expected: All containers should show ports without errors

---

## ✓ 6. Internal Network Configuration

- [ ] team-internal network exists
  ```bash
  docker network ls | grep team-internal
  ```
  Expected: Network "team-internal" should be listed

- [ ] All services are on team-internal network
  ```bash
  docker network inspect team-internal
  ```
  Expected: All three containers (api, ai-service, db) should be connected

- [ ] API can reach AI Service via DNS
  ```bash
  docker compose exec api ping -c 3 ai-service
  ```
  Expected: Should get responses from ai-service

- [ ] API can reach DB via DNS
  ```bash
  docker compose exec api ping -c 3 db
  ```
  Expected: Should get responses from db

- [ ] Services can communicate internally
  ```bash
  # Test API -> AI Service
  docker compose exec api curl -s http://ai-service:9000/health | grep -q "ok" && echo "✓ Connected"
  
  # Test API -> DB (if psql client available)
  docker compose exec api pg_isready -U iotuser -h db -d iotdb
  ```
  Expected: Both should succeed

- [ ] Dependency order is correct
  ```bash
  docker compose logs api | grep -i "ai-service\|db" | head -5
  ```
  Expected: API should start after ai-service and db are healthy

---

## Summary Checklist

- [ ] Database (PostgreSQL 16 Alpine) is running and healthy
- [ ] AI Service (FastAPI mock) is running on port 9000 with /health and /predict
- [ ] API Service (FastAPI) is running on port 8000 with /health and /readings
- [ ] Bearer token validation works correctly
- [ ] All ports are accessible and not conflicting
- [ ] All services are on team-internal network and can communicate
- [ ] Database healthcheck uses pg_isready
- [ ] API has proper dependency order (depends_on with condition service_healthy)
- [ ] Non-root user (appuser) is used in container
- [ ] All sensitive config is in .env (not hardcoded)

---

## Deployment Readiness Status

When all checkmarks are complete:

✅ **READY FOR TESTING**

The system is ready for:
- Postman collection testing
- Integration testing
- Performance testing
- Production-like environment testing

If any check fails, review logs:
```bash
docker compose logs -f
docker compose logs <service-name>
```

---

## Quick Health Check Command

Run this to verify everything in one go:

```bash
#!/bin/bash
echo "=== Service Status ===" && docker compose ps && \
echo "" && echo "=== API Health ===" && curl -s http://localhost:8000/health && \
echo "" && echo "=== AI Health ===" && curl -s http://localhost:9000/health && \
echo "" && echo "=== DB Health ===" && docker compose exec db pg_isready -U iotuser -d iotdb && \
echo "" && echo "=== Network ===" && docker network inspect team-internal | grep -A 5 "Containers"
```

Save as `health-check.sh` and run with `bash health-check.sh`
