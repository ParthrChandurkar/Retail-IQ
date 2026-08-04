.PHONY: up down download-data etl analytics-reports train test

up:
	docker compose up -d

down:
	docker compose down

download-data:
	@echo "not yet implemented — Phase 2"

etl:
	@echo "not yet implemented — Phase 2"

analytics-reports:
	@echo "not yet implemented — Phase 3"

train:
	@echo "not yet implemented — Phase 6"

test:
	@echo "not yet implemented — Phase 8"
