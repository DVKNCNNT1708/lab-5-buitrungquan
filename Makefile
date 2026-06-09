.PHONY: help compose-up compose-down logs ps test-compose clean

help:
	@echo "FIT4110 Lab 05: Docker Compose Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make compose-up      - Build and start all services"
	@echo "  make compose-down    - Stop and remove all services"
	@echo "  make logs            - View logs from all services"
	@echo "  make ps              - Show running containers"
	@echo "  make test-compose    - Run Postman tests"
	@echo "  make clean           - Clean up containers and volumes"

compose-up:
	@echo "Building and starting Docker Compose services..."
	docker compose up -d --build
	@echo "Waiting for services to be healthy..."
	@sleep 5
	docker compose ps

compose-down:
	@echo "Stopping and removing Docker Compose services..."
	docker compose down

logs:
	@echo "Showing logs from all services..."
	docker compose logs -f

ps:
	@echo "Running containers:"
	docker compose ps

test-compose:
	@echo "Running Postman collection tests..."
	@if [ -f "postman/collections/FIT4110_lab05_iot_compose.postman_collection.json" ]; then \
		mkdir -p reports; \
		docker run --rm \
			--network host \
			-v $(PWD)/postman:/etc/postman \
			-v $(PWD)/reports:/reports \
			postman/newman:latest run \
			/etc/postman/collections/FIT4110_lab05_iot_compose.postman_collection.json \
			-e /etc/postman/environments/FIT4110_lab05_local.postman_environment.json \
			-r json,html \
			--reporter-html-export /reports/newman-report.html \
			--reporter-json-export /reports/newman-report.json; \
		echo "Report saved to reports/newman-report.html"; \
	else \
		echo "Postman collection not found"; \
	fi

clean:
	@echo "Cleaning up containers and volumes..."
	docker compose down -v
	@echo "Cleanup complete"
