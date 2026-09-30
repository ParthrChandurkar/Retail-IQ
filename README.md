# Retail IQ

Retail IQ is a retail business-intelligence and machine-learning platform built around an Indian store-sales dataset. It ingests and validates CSV data, builds governed PostgreSQL marts, serves analytics and classification APIs, and presents the results through a Next.js dashboard and Power BI assets.

## Features

- Idempotent raw-data ingestion and data-quality reporting
- Cleaning, feature engineering, and audited curated tables
- Pre-aggregated dashboard marts with shared metric definitions
- Executive, sales, customer, product, regional, and statistical views
- High-profit-order classification and model registry
- JWT authentication with rotating refresh-cookie support
- Power BI measures and a restricted reporting database role
- Automated backend, frontend, accessibility, browser, and container checks

## Architecture

```text
Indian retail CSV
        |
        v
Raw ingestion and quality checks
        |
        v
Cleaning, validation, and feature engineering
        |
        v
Curated PostgreSQL entities and audit records
        |
        +--> Dashboard marts --> FastAPI --> Next.js
        |
        +--> Analytics and ML --> Reports and model registry
        |
        +--> Read-only marts --> Power BI
```

See [`docs/architecture.md`](docs/architecture.md) for data grains, trust boundaries, and the entity model.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS, React Query, Recharts, React Leaflet |
| Backend | Python 3.11, FastAPI, Pydantic, SQLAlchemy, asyncpg |
| Database | PostgreSQL and Alembic |
| Analytics | pandas, SciPy, Matplotlib, Seaborn, Jupyter |
| Machine learning | scikit-learn, XGBoost, joblib |
| Testing and quality | pytest, Ruff, mypy, Vitest, Testing Library, Playwright, axe-core |
| Delivery | Docker Compose and GitHub Actions |
| Business intelligence | Power BI Desktop and DAX |

## Getting Started

Prerequisites: Git, Docker with the Compose plugin, and enough local memory for PostgreSQL, the frontend, the backend, and model training. GNU Make is optional.

Copy the service environment examples:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

Set non-default local values for at least `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and `POWERBI_READER_PASSWORD`. Never commit populated environment files.

Start the services:

```bash
docker compose up -d
docker compose ps
```

Default interfaces:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- OpenAPI documentation: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

## Dataset

Follow [`data/README.md`](data/README.md) for the current source, expected filename, schema checks, and integrity guidance. Kaggle credentials are needed only for automated download and must be supplied through the environment.

After the source file is available, build the data product:

```bash
make etl
make analytics-reports
make train
```

The `Makefile` contains the equivalent Docker Compose commands. On Windows without GNU Make, run those commands directly.

## Usage

Sign in with the administrator account configured in `backend/.env`. The frontend provides filtered dashboard views and a single-order classification workflow. Power BI guidance and measures are under [`powerbi/`](powerbi/).

## Testing

```bash
make test
```

This runs backend formatting, linting, typing, and pytest checks in Docker, followed by frontend linting, type checking, and unit tests. The GitHub Actions workflow adds the browser, accessibility, and image-build checks defined in the repository.

## Configuration

The backend example documents database, authentication, Kaggle, reporting, model-registry, CORS, and Power BI reader settings. The frontend example controls the public API base URL. Use separate strong credentials for application administration and read-only BI access.

## Limitations

- Full operation requires the separately acquired dataset and completed ETL pipeline.
- Power BI viewing or authoring requires Power BI Desktop; the repository provides supporting files and measures rather than a hosted BI service.
- Classification results depend on the checked-in pipeline, source data, and selected target definition.
- This is a portfolio and academic analytics system, not a managed production data platform.

