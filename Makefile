.PHONY: up down download-data etl analytics-reports train test

up:
	docker compose up -d

down:
	docker compose down

download-data:
	docker compose run --rm --no-deps \
		-e KAGGLE_USERNAME="$(KAGGLE_USERNAME)" \
		-e KAGGLE_KEY="$(KAGGLE_KEY)" \
		backend python -m app.etl.download_data

etl:
	docker compose run --rm backend alembic upgrade head
	docker compose run --rm \
		-e GIT_COMMIT="$(shell git rev-parse HEAD)" \
		backend python -m app.etl.run_all

analytics-reports:
	docker compose run --rm backend alembic upgrade head
	docker compose run --rm backend python -m app.etl.build_marts
	docker compose run --rm \
		-e GIT_COMMIT="$(shell git rev-parse HEAD)" \
		backend python -m app.analytics.generate_reports

train:
	@echo "not yet implemented — Phase 6"

test:
	@echo "not yet implemented — Phase 8"
