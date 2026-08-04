# Retail Business Intelligence Platform
## Software Requirements Specification & Implementation Plan

**Document Type:** Engineering SRS + Build Plan (for autonomous/AI-assisted implementation)
**Project Codename:** `retail-bi-platform`
**Version:** 1.0
**Classification:** Internal — Engineering / Build Specification

**Purpose of this document:** This document is written to be handed directly to an AI coding agent (e.g. Codex) as the single source of truth for building the entire system from an empty repository. Every section is written to be unambiguous and directly actionable: schemas are complete, folder structures are literal, API contracts are explicit, and each implementation phase has a defined scope, deliverable, and exit criteria. Where a decision must be data-driven rather than pre-specified (notably, the ML target variable), this document defines the **decision framework** rather than the decision itself, and requires the agent to produce a documented decision artifact before proceeding.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Goals & Non-Goals](#2-goals--non-goals)
3. [Target Users & Personas](#3-target-users--personas)
4. [Dataset Specification](#4-dataset-specification)
5. [Data Science Methodology & Target Variable Decision Framework](#5-data-science-methodology--target-variable-decision-framework)
6. [System Architecture](#6-system-architecture)
7. [Technology Stack](#7-technology-stack)
8. [Database Design](#8-database-design)
9. [API Specification](#9-api-specification)
10. [Frontend Architecture](#10-frontend-architecture)
11. [UI/UX Design System](#11-uiux-design-system)
12. [Analytics & Statistical Modules](#12-analytics--statistical-modules)
13. [Machine Learning Pipeline](#13-machine-learning-pipeline)
14. [Optional NLP Module](#14-optional-nlp-module)
15. [Repository & Folder Structure](#15-repository--folder-structure)
16. [Non-Functional Requirements](#16-non-functional-requirements)
17. [Implementation Phases (Build Plan)](#17-implementation-phases-build-plan)
18. [Testing Strategy](#18-testing-strategy)
19. [Deployment & DevOps](#19-deployment--devops)
20. [README Specification](#20-readme-specification)
21. [Appendix](#21-appendix)

---

## 1. Executive Summary

The Retail Business Intelligence Platform is a production-grade analytics application that transforms raw e-commerce transaction data into decision-ready insight for retail management. It is built around three pillars, in order of priority:

| Priority | Pillar | Description |
|---|---|---|
| 1 (Primary) | **Business & Customer Analytics** | Descriptive and diagnostic analytics: revenue, sales trends, customer segmentation, RFM, regional performance, delivery/payment behaviour. |
| 2 (Primary) | **Statistical Analysis & Visualization** | Rigorous statistical validation (hypothesis testing, correlation, distribution analysis) surfaced through an interactive BI dashboard. |
| 3 (Supporting) | **Classification (Machine Learning)** | A single, data-justified classification model that predicts a business-relevant outcome, selected only after EDA — not fixed in advance. |

The system is **not** a machine-learning showcase. ML is one supporting capability among many, deliberately scoped to a single, well-justified classification task so that analytics, statistics, and visualization remain the visible center of gravity of the product.

The platform is delivered as a decoupled system: a Next.js/TypeScript frontend consuming a versioned REST API served by a FastAPI backend, backed by PostgreSQL, with a Python analytics/ML layer that can run both as batch jobs (notebooks, scheduled feature/model builds) and as callable services behind the API.

---

## 2. Goals & Non-Goals

### 2.1 Goals

- Ingest and model the Olist Brazilian E-Commerce dataset in a normalized, query-efficient relational schema.
- Produce a full descriptive analytics layer: revenue, orders, customers, products, sellers, regions, payments, delivery, reviews.
- Produce a customer analytics layer: segmentation, RFM, CLV, repeat-purchase behaviour, demographics/regional behaviour.
- Produce a statistical analysis layer: descriptive statistics, correlation/covariance, and hypothesis tests (Chi-Square, ANOVA, T-Test) exposed as first-class, explained results — not just numbers.
- Select and justify **one** classification target using a documented, criteria-based process (Section 5), then build, compare, and explain multiple candidate models against it.
- Deliver a multi-page, interactive, filterable BI dashboard that reads like a commercial analytics product (Power BI / Tableau / Stripe Dashboard class of UI), not a static report.
- Auto-generate plain-language business recommendations from the analytics and model outputs.
- Ship clean, typed, tested, documented, containerized code organized for a small team to extend.

### 2.2 Non-Goals

- This is **not** a real-time streaming analytics system — batch/near-real-time (scheduled refresh) is sufficient.
- This is **not** a multi-tenant SaaS product — single-tenant, single-dataset deployment is in scope; multi-tenancy is a documented future-scope item only.
- This is **not** an ML research project — no custom model architectures, no deep learning; classical ML (Logistic Regression → Gradient Boosting/XGBoost) is sufficient and preferred for explainability.
- NLP/review-sentiment (Section 14) is **optional** and only built if the review-text data is of sufficient quality/volume to justify it — this too is a data-gated decision, not an assumption.

---

## 3. Target Users & Personas

| Persona | Primary Goal | Key Dashboards | Core Questions They Ask |
|---|---|---|---|
| **Executive (C-level)** | High-level performance snapshot | Dashboard (home), Insights | "Is revenue growing? Where are we losing money? What should we prioritize this quarter?" |
| **Retail / Store Manager** | Operational performance by region/store | Regional Dashboard, Product Dashboard | "Which regions/categories are underperforming? Where are delivery delays concentrated?" |
| **Business Analyst** | Deep-dive, cross-filtering, statistical rigor | Analytics Dashboard, Customer Dashboard | "Is the difference in satisfaction between payment methods statistically significant? What correlates with repeat purchase?" |
| **Marketing Team** | Customer understanding & targeting | Customer Dashboard, Insights Dashboard | "Who are our high-value customers? Which segment should we target this campaign at?" |
| **Sales Manager** | Product & seller performance | Sales Dashboard, Product Dashboard | "What are the top products/categories? Which sellers are top/under performers?" |
| **Data/BI Team (internal)** | Model transparency & governance | Classification Dashboard, Settings | "Why did the model predict this? Which features matter? How was the target variable chosen?" |

Each persona maps to at least one page in Section 10.2 (Pages). Every dashboard must support the shared filter bar (Section 9.6 / interactive filters) so personas can self-serve rather than requesting custom cuts.

---

## 4. Dataset Specification

**Source:** Brazilian E-Commerce Public Dataset by Olist — Kaggle (`olistbr/brazilian-ecommerce`).
**Scale:** ~100,000 orders, 2016–2018, 9 relational CSV files.

The agent must treat the raw CSVs as the **immutable source layer**. All cleaning/transformation happens downstream (Section 8.1 — raw vs. curated schema separation). The table below is the contract the ingestion layer must satisfy.

| Source File | Approx. Rows | Grain | Key Columns | Known Data-Quality Risks to Check |
|---|---|---|---|---|
| `olist_customers_dataset.csv` | ~99K | 1 row / customer id | `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state` | `customer_id` vs `customer_unique_id` distinction (one real customer can have multiple `customer_id`s — critical for repeat-purchase/CLV logic) |
| `olist_orders_dataset.csv` | ~99K | 1 row / order | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date` | Null delivery timestamps for non-delivered orders; timestamp ordering violations; timezone consistency |
| `olist_order_items_dataset.csv` | ~112K | 1 row / item within order | `order_id`, `order_item_id`, `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value` | Multiple items per order (must aggregate correctly for order-level revenue) |
| `olist_products_dataset.csv` | ~33K | 1 row / product | `product_id`, `product_category_name`, dimension/weight columns | Missing category names; missing dimensions/weights |
| `olist_sellers_dataset.csv` | ~3K | 1 row / seller | `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state` | — |
| `olist_order_payments_dataset.csv` | ~104K | 1+ rows / order (installments/split payment) | `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value` | Multiple payment rows per order must be aggregated before joining 1:1 to orders |
| `olist_order_reviews_dataset.csv` | ~99K | 1 row / review | `review_id`, `order_id`, `review_score`, `review_comment_title`, `review_comment_message`, timestamps | High null rate on comment text/title (drives the NLP go/no-go decision in Section 14); duplicate reviews per order |
| `olist_geolocation_dataset.csv` | ~1M | many rows / zip prefix | `geolocation_zip_code_prefix`, `lat`, `lng`, `city`, `state` | Many-to-many zip↔lat/lng (must reduce to one representative point per zip prefix, e.g. median) |
| `product_category_name_translation.csv` | ~71 | 1 row / category | `product_category_name`, `product_category_name_english` | Categories present in `products` but absent from translation table |

### 4.1 Ingestion Contract

- Raw files are loaded byte-for-byte into a `raw.*` schema (Section 8.1) with no transformation except column typing.
- A single, versioned ingestion script (`backend/app/etl/ingest.py`) must be idempotent — re-running it must not duplicate rows.
- A **Data Quality Report** (generated artifact, Section 5.2, Step 2) must be produced immediately after ingestion and before any cleaning logic is written, quantifying: null rates per column, duplicate rates per grain, referential-integrity violations (orphaned foreign keys across the 9 files), and outlier flags on `price`, `freight_value`, `payment_value`, delivery duration.

---

## 5. Data Science Methodology & Target Variable Decision Framework

This section is the most important constraint in the document: **the classification target must not be hard-coded by the agent.** It must be *derived* through the staged process below, and the derivation must be committed to the repository as a artifact (`analytics/reports/target_variable_selection.md`) before any model-training code is written. A build that skips straight to modeling a pre-chosen target fails this specification.

### 5.1 Why this constraint exists

The brief explicitly requires that classification supports business analytics rather than the reverse. Choosing the target only after cleaning, EDA, and correlation/statistical analysis ensures the eventual model is the one best supported by the data — not the one that happened to sound interesting.

### 5.2 Mandatory staged process

| Stage | Name | Must Produce | Gate to Next Stage |
|---|---|---|---|
| 1 | Data Cleaning | Cleaned/curated tables (Section 8.1), cleaning log | No further null/duplicate/outlier issues above documented thresholds |
| 2 | Data Quality Report | `analytics/reports/data_quality_report.md` (null %, dup %, orphan FK %, outlier counts per numeric column) | Report reviewed; thresholds documented |
| 3 | Exploratory Data Analysis | Univariate, bivariate, multivariate notebooks/reports (Section 12.1) | Key distributions and relationships documented with charts |
| 4 | Statistical Analysis | Correlation matrix, covariance, and at least one Chi-Square, one ANOVA, one T-Test with stated null hypothesis, statistic, p-value, and plain-language conclusion (Section 12.2) | Statistically meaningful candidate features identified |
| 5 | Candidate Target Evaluation | Scoring matrix (Section 5.3) for all 4 candidate targets | Highest-scoring, feasible candidate identified |
| 6 | Target Selection Report | `analytics/reports/target_variable_selection.md` — states the chosen target, the scores, and the rationale in business language | Signed off (documented) before Phase 6 (ML) begins |

### 5.3 Candidate Targets & Scoring Rubric

The four candidates named in the brief must each be scored 1 (poor) – 5 (excellent) on the five criteria below. The agent computes these scores from the actual cleaned data (they are not to be assumed) and records the numbers in the report.

| Candidate Target | Definition | Data Availability | Class Balance | Business Value | Feature Support (correlation strength found in Stage 4) | Feasibility |
|---|---|---|---|---|---|---|
| **Repeat Customer Prediction** | Will a customer (`customer_unique_id`) place a second order within N months? | Must check: how many unique customers actually have 2+ orders — historically low in this dataset (~3%), which risks severe class imbalance | Score based on actual measured ratio | High — retention is a core retail lever | Based on RFM/behavioural features found predictive in Stage 4 | Consider need for resampling (SMOTE/class-weighting) |
| **Customer Satisfaction Classification** | Predict review_score bucket (e.g. low ⩽3 vs high ⩾4) from order/delivery/product features, *excluding* review text | `review_score` has good coverage (~99% of delivered orders) | Typically skewed toward high scores — measure actual split | High — satisfaction drives retention & brand | Delivery delay, price, freight, category historically correlate | Generally most feasible of the four |
| **Late Delivery Classification** | Predict whether `order_delivered_customer_date > order_estimated_delivery_date` | Requires both dates non-null — measure actual coverage | Measure actual on-time vs. late ratio | High — operational/logistics lever | Seller, distance (via geolocation), category, freight typically correlate | High — clear binary label, no leakage risk if features are pre-delivery only |
| **High-Value Customer Classification** | Predict whether a customer's CLV/order value places them in the top X% | Requires CLV computed in Stage 1/7 (Section 12.3) | Depends on chosen threshold (e.g. top 20%) — tune to avoid trivial imbalance | High — targeting/segmentation lever | Order frequency, AOV, category mix | Medium — definition of "high value" must be fixed and documented first |

**Decision rule:** compute the row-wise sum (or weighted sum, weights documented) of the five scores for each candidate; select the maximum. If two candidates are within 1 point, prefer the one with better class balance and lower leakage risk (a model must only use features available *before* the outcome is known — e.g. Late Delivery must not use post-delivery fields). Document the tie-break explicitly if invoked.

> **Historical note for the implementer:** across public analyses of this dataset, *Late Delivery Classification* and *Customer Satisfaction Classification* are typically the two strongest candidates on data availability and feasibility. This note does not pre-select the target — the scoring in Stage 5 is still mandatory and must be computed from this project's own cleaned data — but it should not surprise the implementer if one of those two wins.

### 5.4 Deliverable Template

`analytics/reports/target_variable_selection.md` must contain, at minimum: the scoring table with actual computed numbers, the selected target with its precise operational definition (e.g. exact cutoff dates/thresholds), the list of features excluded for leakage, and a one-paragraph business justification suitable for showing to a non-technical stakeholder.


---

## 6. System Architecture

### 6.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                            │
│   Next.js 14 (App Router) · TypeScript · React Query · Tailwind      │
└───────────────────────────────┬────────────────────────────────────-─┘
                                 │  HTTPS / JSON (REST, versioned /api/v1)
                                 ▼
┌────────────────────────────────────────────────────────────────────--┐
│                              API LAYER                               │
│   FastAPI · Pydantic v2 schemas · JWT auth · rate limiting            │
│   Routers: dashboard · customers · products · sellers · regions ·    │
│            payments · reviews · classification · analytics · admin   │
└───────────────────────────────┬──────────────────────────────────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 ▼                                ▼
┌────────────────────────────────┐   ┌─────────────────────────────────┐
│        ANALYTICS ENGINE        │   │      ML / CLASSIFICATION        │
│  Pandas/NumPy transforms       │   │  Scikit-Learn + XGBoost models  │
│  RFM, CLV, statistical tests   │   │  Trained offline → serialized   │
│  (SciPy) — service layer       │   │  (joblib) → served via API      │
│  called by API layer           │   │  Model registry + metrics store │
└───────────────────────────────-┘   └─────────────────────────────────┘
                 │                                │
                 └───────────────┬────────────────┘
                                 ▼
┌────────────────────────────────────────────────────────────────────--┐
│                              DATA LAYER                               │
│   PostgreSQL 15+  ·  schemas: raw / curated / marts / ml               │
│   SQLAlchemy 2.0 ORM · Alembic migrations                             │
└────────────────────────────────────────────────────────────────────--┘
```

This satisfies the brief's architecture chain (`Frontend → REST API → Backend → Analytics Engine → ML Module → Database`) while keeping Analytics and ML as **sibling services behind the same API layer**, not a strict pipeline — the API must be able to serve pure analytics (no ML involved) and pure ML results independently, since ML is a supporting capability, not a bottleneck for the rest of the product.

### 6.2 Request Flow (example)

1. Frontend dashboard page mounts → React Query fires `GET /api/v1/dashboard/summary?date_from=...&state=...`.
2. FastAPI router validates query params via a Pydantic model, resolves filters into a SQL predicate.
3. Router calls the **Analytics Service** (`app/services/analytics_service.py`), which queries the `marts` schema (pre-aggregated tables — Section 8.3), not raw tables, for performance.
4. Service returns a typed Pydantic response model; FastAPI serializes to JSON.
5. Frontend's typed API client (generated types from OpenAPI, Section 9.1) deserializes into typed React Query cache; Recharts renders.

### 6.3 Batch/Offline Flow (ETL + ML training)

1. `make etl` / `python -m app.etl.run_all` → ingest raw CSVs → clean → curate → build marts (Section 8) → refresh materialized views.
2. `make analytics-reports` → generates the Stage 1–5 reports from Section 5.2 into `analytics/reports/`.
3. `make train` (only runs after `target_variable_selection.md` exists and is checked into the repo) → trains and compares candidate algorithms (Section 13), serializes the winning model + metrics to `ml/registry/`.
4. API's classification router loads the latest registered model at startup (or on demand) and serves predictions/explanations without retraining inline.

---

## 7. Technology Stack

### 7.1 Frontend

| Concern | Choice | Notes |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR for landing/overview pages, CSR for interactive dashboards |
| Language | TypeScript (strict mode) | No `any` in application code |
| Styling | Tailwind CSS | Design tokens per Section 11 |
| Components | shadcn/ui | Headless, accessible primitives, themed to design system |
| Animation | Framer Motion | Page transitions, card entrance, chart micro-interactions — used sparingly |
| Data fetching/cache | React Query (TanStack Query) | All server state; no ad-hoc `useEffect` fetches |
| Charts | Recharts | Line, bar, area, pie/donut, treemap |
| Maps | Leaflet (+ `react-leaflet`) | Regional/geolocation choropleth & point maps |
| Forms/validation | React Hook Form + Zod | Settings, login, filter forms |
| State (client/UI only) | Zustand | Filter bar state, theme, sidebar — not server data |

### 7.2 Backend

| Concern | Choice | Notes |
|---|---|---|
| Framework | FastAPI | Async, OpenAPI auto-generated, Pydantic-native |
| Validation/schemas | Pydantic v2 | Request/response models for every endpoint |
| ORM | SQLAlchemy 2.0 (async) | Typed models mirroring Section 8 schema |
| Migrations | Alembic | One migration per schema change, checked into `backend/alembic/versions` |
| Data processing | Pandas, NumPy | ETL + analytics transforms |
| Stats | SciPy (`scipy.stats`) | Chi-Square, ANOVA, T-Test |
| ML | Scikit-Learn, XGBoost | Section 13 |
| Explainability | SHAP (optional) | Feature importance is mandatory; SHAP is a stretch goal |
| NLP (optional) | NLTK, TextBlob | Only if Section 14 gate passes |
| Auth | `python-jose` (JWT) + `passlib` (bcrypt) | Simple email/password auth sufficient for v1 |
| Background/scheduled jobs | APScheduler (or a simple cron-triggered script) | Nightly marts refresh |

### 7.3 Data & Infra

| Concern | Choice | Notes |
|---|---|---|
| Database | PostgreSQL 15+ | Schemas: `raw`, `curated`, `marts`, `ml` |
| Notebooks | Jupyter | EDA/statistics/model development, mirrored into `analytics/notebooks/` |
| Optional BI | Power BI | Optional export path for stakeholders who want native Power BI, not a replacement for the web dashboard |
| Plotting (notebooks) | Matplotlib, Plotly | Exploratory only; production charts are Recharts in the frontend |
| Containerization | Docker + Docker Compose | `frontend`, `backend`, `db`, (optional `pgadmin`) services |
| Source control | Git + GitHub | Trunk-based, PR + CI checks (Section 18/19) |
| CI | GitHub Actions | Lint, type-check, test, build on every PR |

### 7.4 Versions (pin in `package.json` / `pyproject.toml`)

Use current stable major versions at implementation time (Next.js 14.x, React 18.x, FastAPI ≥0.110, SQLAlchemy ≥2.0, Pydantic ≥2.6, Python ≥3.11, Node ≥20 LTS). Do not use deprecated Pydantic v1 syntax or the Next.js Pages Router.

---

## 8. Database Design

### 8.1 Schema Strategy — four PostgreSQL schemas in one database

| Schema | Purpose | Written By | Read By |
|---|---|---|---|
| `raw` | 1:1 mirror of the 9 source CSVs, typed but untransformed | ETL ingestion step | ETL cleaning step only |
| `curated` | Cleaned, deduplicated, standardized entities (one table per business entity) | ETL cleaning step | Analytics service, ML feature builder |
| `marts` | Pre-aggregated, query-optimized tables/materialized views built *for* specific dashboards | Analytics batch job | API routers (read-only, hot path) |
| `ml` | Model registry metadata, feature snapshots, predictions, evaluation metrics | ML training job | Classification API router |

This separation exists so the interactive dashboard never runs expensive joins/aggregations against raw-shaped data on the request path — `marts` tables are the only thing the live API touches for chart data.

### 8.2 `curated` Schema — Core Entity Tables

```sql
-- curated.customers  (deduplicated at customer_unique_id grain for analytics,
--                      but customer_id kept for order linkage)
CREATE TABLE curated.customers (
    customer_id            VARCHAR PRIMARY KEY,
    customer_unique_id     VARCHAR NOT NULL,
    zip_code_prefix        VARCHAR,
    city                    VARCHAR,
    state                   VARCHAR(2),
    latitude                DOUBLE PRECISION,
    longitude               DOUBLE PRECISION
);
CREATE INDEX ix_customers_unique_id ON curated.customers (customer_unique_id);

-- curated.orders
CREATE TABLE curated.orders (
    order_id                    VARCHAR PRIMARY KEY,
    customer_id                 VARCHAR NOT NULL REFERENCES curated.customers(customer_id),
    order_status                VARCHAR NOT NULL,
    purchase_ts                 TIMESTAMP NOT NULL,
    approved_ts                 TIMESTAMP,
    delivered_carrier_ts        TIMESTAMP,
    delivered_customer_ts       TIMESTAMP,
    estimated_delivery_ts       TIMESTAMP,
    is_late                     BOOLEAN,          -- derived, nullable until delivered
    delivery_days               INTEGER,          -- derived
    delivery_delay_days         INTEGER           -- derived, delivered - estimated
);
CREATE INDEX ix_orders_customer ON curated.orders (customer_id);
CREATE INDEX ix_orders_purchase_ts ON curated.orders (purchase_ts);
CREATE INDEX ix_orders_status ON curated.orders (order_status);

-- curated.products
CREATE TABLE curated.products (
    product_id                  VARCHAR PRIMARY KEY,
    category_name               VARCHAR,
    category_name_english       VARCHAR,
    weight_g                    NUMERIC,
    length_cm                   NUMERIC,
    height_cm                   NUMERIC,
    width_cm                    NUMERIC
);

-- curated.sellers
CREATE TABLE curated.sellers (
    seller_id                   VARCHAR PRIMARY KEY,
    zip_code_prefix             VARCHAR,
    city                         VARCHAR,
    state                        VARCHAR(2),
    latitude                     DOUBLE PRECISION,
    longitude                    DOUBLE PRECISION
);

-- curated.order_items
CREATE TABLE curated.order_items (
    order_id                    VARCHAR NOT NULL REFERENCES curated.orders(order_id),
    order_item_id               INTEGER NOT NULL,
    product_id                  VARCHAR NOT NULL REFERENCES curated.products(product_id),
    seller_id                   VARCHAR NOT NULL REFERENCES curated.sellers(seller_id),
    price                        NUMERIC NOT NULL,
    freight_value                NUMERIC NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

-- curated.payments  (aggregated to one row per order for convenience,
--                     raw per-installment detail retained in raw schema)
CREATE TABLE curated.payments (
    order_id                    VARCHAR PRIMARY KEY REFERENCES curated.orders(order_id),
    primary_payment_type        VARCHAR,
    installments_max             INTEGER,
    total_payment_value          NUMERIC
);

-- curated.reviews
CREATE TABLE curated.reviews (
    review_id                   VARCHAR PRIMARY KEY,
    order_id                    VARCHAR NOT NULL REFERENCES curated.orders(order_id),
    review_score                 SMALLINT NOT NULL CHECK (review_score BETWEEN 1 AND 5),
    comment_title                 TEXT,
    comment_message               TEXT,
    review_creation_ts             TIMESTAMP,
    review_answer_ts               TIMESTAMP
);
```

### 8.3 `marts` Schema — Dashboard-Facing Aggregates (representative subset)

| Table / Materialized View | Grain | Feeds | Refresh |
|---|---|---|---|
| `marts.revenue_daily` | date | Sales Dashboard trend chart, Dashboard KPI cards | Nightly |
| `marts.revenue_by_category` | category | Product Dashboard | Nightly |
| `marts.revenue_by_region` | state | Regional Dashboard, map | Nightly |
| `marts.customer_rfm` | customer_unique_id | Customer Dashboard, segmentation | Nightly |
| `marts.customer_segments` | segment | Customer Dashboard KPI cards | Nightly |
| `marts.seller_performance` | seller_id | Product/Regional Dashboard | Nightly |
| `marts.payment_method_mix` | payment_type | Dashboard, Analytics Dashboard | Nightly |
| `marts.delivery_performance` | state / category | Regional Dashboard, Analytics Dashboard | Nightly |
| `marts.review_summary` | category / seller / month | Insights Dashboard | Nightly |
| `marts.kpi_snapshot` | single row, latest | Dashboard home KPI cards | Nightly |

### 8.4 `ml` Schema

```sql
CREATE TABLE ml.model_registry (
    model_id           SERIAL PRIMARY KEY,
    target_variable     VARCHAR NOT NULL,     -- e.g. 'late_delivery'
    algorithm            VARCHAR NOT NULL,     -- e.g. 'xgboost'
    trained_at           TIMESTAMP NOT NULL,
    is_active            BOOLEAN DEFAULT FALSE,
    artifact_path         VARCHAR NOT NULL,     -- path to joblib file
    metrics_json           JSONB NOT NULL        -- accuracy/precision/recall/f1/roc_auc/cv scores
);

CREATE TABLE ml.predictions (
    id                  SERIAL PRIMARY KEY,
    model_id             INTEGER REFERENCES ml.model_registry(model_id),
    entity_id             VARCHAR NOT NULL,     -- order_id or customer_id depending on target
    predicted_label        VARCHAR NOT NULL,
    predicted_probability   NUMERIC,
    created_at             TIMESTAMP DEFAULT now()
);

CREATE TABLE ml.feature_importance (
    model_id             INTEGER REFERENCES ml.model_registry(model_id),
    feature_name          VARCHAR NOT NULL,
    importance             NUMERIC NOT NULL
);
```

---

## 9. API Specification

**Base path:** `/api/v1`. All responses are JSON; all list endpoints support pagination (`page`, `page_size`) and the shared filter query params in Section 9.6. OpenAPI schema is auto-generated by FastAPI at `/api/v1/openapi.json` and must be used to generate the frontend's typed API client (do not hand-write duplicate frontend types).

### 9.1 Conventions

- Versioned prefix: `/api/v1/...`
- Auth: `Authorization: Bearer <JWT>` on all routes except `/auth/*` and `/health`.
- Errors: RFC 7807-style problem JSON — `{ "detail": string, "code": string }` with correct HTTP status.
- Every response includes `generated_at` (ISO timestamp) so the frontend can show "data as of" freshness.

### 9.2 Auth

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Email/password → JWT |
| POST | `/auth/refresh` | Refresh token → new JWT |
| GET | `/auth/me` | Current user profile |

### 9.3 Dashboard (home / cross-cutting KPIs)

| Method | Path | Description |
|---|---|---|
| GET | `/dashboard/summary` | Total revenue, orders, customers, AOV, MoM/YoY growth — reads `marts.kpi_snapshot` |
| GET | `/dashboard/revenue-trend` | Time series for the trend chart (`marts.revenue_daily`) |
| GET | `/dashboard/top-products` | Top N products by revenue/units |
| GET | `/dashboard/top-categories` | Top N categories |
| GET | `/dashboard/top-sellers` | Top N sellers |

### 9.4 Domain Routers

| Router | Representative Endpoints |
|---|---|
| `/customers` | `GET /customers/segments`, `GET /customers/rfm`, `GET /customers/{customer_unique_id}`, `GET /customers/clv-distribution`, `GET /customers/repeat-purchase-rate` |
| `/products` | `GET /products/performance`, `GET /products/categories`, `GET /products/{product_id}` |
| `/sellers` | `GET /sellers/performance`, `GET /sellers/{seller_id}` |
| `/regions` | `GET /regions/sales`, `GET /regions/geo` (lat/lng points for Leaflet), `GET /regions/delivery-performance` |
| `/payments` | `GET /payments/method-mix`, `GET /payments/installments-distribution` |
| `/reviews` | `GET /reviews/score-distribution`, `GET /reviews/trends`, `GET /reviews/nlp-summary` (only if Section 14 gate passes) |
| `/analytics` | `GET /analytics/correlation-matrix`, `GET /analytics/hypothesis-tests`, `GET /analytics/descriptive-stats`, `GET /analytics/seasonality` |
| `/classification` | `GET /classification/model-info`, `GET /classification/metrics`, `GET /classification/feature-importance`, `POST /classification/predict` |
| `/recommendations` | `GET /recommendations` — returns auto-generated business recommendations (Section 12.4) |
| `/admin` (Settings page) | `GET/PUT /admin/settings`, `GET /admin/data-refresh-status` |

### 9.5 Example Contract — `GET /dashboard/summary`

```json
// Response 200
{
  "generated_at": "2026-08-01T00:00:00Z",
  "total_revenue": 16221836.45,
  "total_orders": 99441,
  "total_customers": 96096,
  "average_order_value": 137.75,
  "revenue_mom_growth_pct": 4.8,
  "revenue_yoy_growth_pct": 21.3
}
```

### 9.6 Shared Filter Query Parameters

Every list/aggregate endpoint accepts the following optional query params, applied server-side against the `marts` tables' pre-joined dimension columns:

`date_from`, `date_to`, `state`, `city`, `category`, `seller_id`, `payment_type`, `customer_segment`, `review_score_min`, `review_score_max`.

The frontend filter bar (Section 10.3) is the single source of these params and must serialize them into the URL query string so dashboard views are shareable/bookmarkable.

---

## 10. Frontend Architecture

### 10.1 Routing Strategy (Next.js App Router)

```
app/
├── (marketing)/
│   ├── page.tsx                  # Landing Page
│   └── overview/page.tsx         # Project Overview
├── (auth)/
│   └── login/page.tsx
├── (app)/                        # authenticated shell — sidebar + topbar layout
│   ├── layout.tsx                # shared shell: sidebar nav, filter bar slot, theme
│   ├── dashboard/page.tsx        # Dashboard (home)
│   ├── dashboard/sales/page.tsx
│   ├── dashboard/customers/page.tsx
│   ├── dashboard/products/page.tsx
│   ├── dashboard/regional/page.tsx
│   ├── dashboard/classification/page.tsx
│   ├── dashboard/analytics/page.tsx
│   ├── dashboard/insights/page.tsx
│   └── settings/page.tsx
└── api/                          # (none — all data comes from the FastAPI backend, not Next.js route handlers, except optional BFF auth proxy)
```

Route groups `(marketing)` and `(auth)` render without the authenticated shell; `(app)` renders inside `layout.tsx`, which hosts the persistent sidebar, topbar (user menu, theme toggle), and the shared filter bar (Section 10.3).

### 10.2 Pages (maps 1:1 to the brief's required page list)

| Page | Route | Primary Components |
|---|---|---|
| Landing Page | `/` | Hero, feature highlights, CTA → Login/Overview |
| Project Overview | `/overview` | Problem statement, dataset summary, architecture diagram (static/marketing content, reuses SRS Section 1/4 content) |
| Login | `/login` | Auth form (React Hook Form + Zod) |
| Dashboard (home) | `/dashboard` | KPI cards, revenue trend, top products/categories/sellers |
| Sales Dashboard | `/dashboard/sales` | Revenue trend, category/product performance, seasonality |
| Customer Dashboard | `/dashboard/customers` | Segments, RFM scatter/table, CLV distribution, repeat-purchase rate, demographics |
| Product Dashboard | `/dashboard/products` | Top products/categories, category treemap, seller performance |
| Regional Dashboard | `/dashboard/regional` | Leaflet map, sales-by-state, delivery performance by region |
| Classification Dashboard | `/dashboard/classification` | Model metrics, confusion matrix, ROC curve, feature importance, single-record predict tool |
| Analytics Dashboard | `/dashboard/analytics` | Correlation heatmap, hypothesis test results, descriptive stats tables |
| Insights Dashboard | `/dashboard/insights` | Auto-generated business recommendations (Section 12.4), review analytics |
| Settings | `/settings` | Theme, account, data refresh status (admin) |

### 10.3 Shared Filter Bar

A single client component (`components/filters/FilterBar.tsx`, Zustand-backed) renders the controls for the params in Section 9.6 (date range, state, city, category, seller, payment method, customer segment, review score range). It is mounted once in the `(app)` layout and every dashboard page subscribes to the relevant subset via a `useFilters()` hook, so filter state persists across dashboard navigation and is reflected in the URL query string.

### 10.4 Component Architecture

```
components/
├── ui/                # shadcn/ui primitives (button, card, select, dialog, tabs, table...)
├── charts/            # thin Recharts wrappers: <RevenueTrendChart/>, <CategoryBarChart/>,
│                       #   <SegmentDonut/>, <CorrelationHeatmap/>, <ConfusionMatrix/>,
│                       #   <ROCCurve/>, <FeatureImportanceBar/>
├── maps/               # <RegionChoroplethMap/>, <SellerPointMap/> (Leaflet wrappers)
├── kpi/                # <KPICard/>, <KPIGrid/>
├── filters/            # <FilterBar/>, <DateRangePicker/>, <MultiSelectFilter/>
├── layout/              # <Sidebar/>, <Topbar/>, <PageHeader/>
├── recommendations/      # <RecommendationCard/>, <RecommendationList/>
└── tables/                # <DataTable/> (sortable/paginated, used by several dashboards)
```

All chart/table components are **presentational** — they receive typed data via props and contain no fetching logic. Each page composes a small number of container components (e.g. `SalesDashboardContainer`) that call typed React Query hooks (`hooks/useDashboardSummary.ts`, `hooks/useCustomerSegments.ts`, ...) which call the generated API client.

### 10.5 State Management Rules

- **Server state** (anything from the API) → React Query only. No duplication into Zustand/Redux.
- **UI/client state** (filters, theme, sidebar collapse) → Zustand.
- **Form state** → React Hook Form, local to the form component.

---

## 11. UI/UX Design System

Reference points: Power BI, Tableau, Stripe Dashboard, Linear, Notion, Vercel. The product must read as a premium analytics SaaS, not a student dashboard template — no default Bootstrap look, no heavy drop shadows, no cartoon iconography.

### 11.1 Design Tokens

| Token | Light Mode | Dark Mode |
|---|---|---|
| `--background` | `#FFFFFF` | `#0B0F17` |
| `--surface` (cards) | `#F7F9FC` | `#131826` |
| `--border` | `#E4E9F0` | `#232A3B` |
| `--primary` | `#1B4F72` (deep blue) | `#3E8ED0` |
| `--primary-foreground` | `#FFFFFF` | `#0B0F17` |
| `--accent` | `#D99A2B` (amber, sparing use — KPI highlights, alerts) | `#D99A2B` |
| `--text-primary` | `#0F172A` | `#E7ECF3` |
| `--text-secondary` | `#5B6472` | `#9AA5B8` |
| `--success` | `#1E8A5F` | `#34C286` |
| `--danger` | `#C0392B` | `#E06258` |

- **Typography:** Inter (UI text), with a monospace (e.g. JetBrains Mono) reserved for numeric/tabular KPI values where alignment matters.
- **Radius:** `--radius: 0.75rem` for cards, `0.5rem` for inputs/buttons — consistent rounded-card language throughout, not mixed sharp/round.
- **Elevation:** flat design by default; use a single soft `box-shadow` tier only on hover/active states and modals — never stacked shadows.
- **Glassmorphism:** applied minimally — only to the topbar and modal overlays (`backdrop-blur` + translucent surface), never to primary content cards, which stay opaque and high-contrast for data legibility.
- **Motion:** Framer Motion used for page-enter fade/slide (150–250ms), card stagger on dashboard mount, and chart tooltip transitions — never for anything that delays a user reading data.
- **Icons:** `lucide-react` throughout (matches the flat, professional line-icon language); no emoji, no cartoon/clipart icon sets.

### 11.2 Layout Grid

- Persistent left sidebar (240px, collapsible to 64px icon rail) + topbar (56px) + content area on a 12-column responsive grid.
- KPI cards: 4-up on desktop, 2-up on tablet, 1-up on mobile.
- Charts: 2-up grid on desktop for paired comparisons (e.g. trend + breakdown), full-width for maps/heatmaps/large tables.

### 11.3 Dark Mode

Full dark mode via `next-themes` + Tailwind `dark:` variants driven by the tokens above — not just an inverted filter. Chart color scales must have distinct light/dark palettes (charts should never render near-invisible series on dark background).

### 11.4 Accessibility

WCAG AA contrast minimum on all text/background pairs in both themes; all interactive elements keyboard-navigable (shadcn/ui provides this by default — do not override focus states); charts must expose data via an accessible table view toggle for screen-reader users on at least the Dashboard home page.

---

## 12. Analytics & Statistical Modules

This section is the functional spec for the **primary** pillar of the product (Section 1). Every sub-module below must be implemented as a backend service function with a corresponding notebook (for the "showing the work" artifact) and a corresponding API endpoint + dashboard visualization (for the product).

### 12.1 Exploratory Data Analysis (backend: `app/services/eda_service.py`, notebook: `analytics/notebooks/02_eda.ipynb`)

| Analysis Type | Required Outputs |
|---|---|
| Univariate | Distribution (histogram) of price, freight_value, payment_value, delivery_days, review_score; summary stats table (mean/median/mode/variance/std) per numeric column |
| Bivariate | Price vs. freight_value scatter; review_score vs. delivery_delay_days boxplot; payment_type vs. average order value bar |
| Multivariate | Correlation matrix across all numeric order/delivery/payment features (rendered as heatmap) |
| Trend | Monthly revenue/orders time series, with simple seasonality decomposition (month-of-year effect) |

### 12.2 Statistical Analysis (backend: `app/services/stats_service.py`, notebook: `03_statistical_analysis.ipynb`)

| Method | Required Use in This Project | Output Shape Returned by API |
|---|---|---|
| Descriptive stats | Mean/median/mode/variance/std/quartiles for all key numeric fields | `{ field, mean, median, mode, std, variance, q1, q3 }[]` |
| Correlation & Covariance | Full numeric correlation matrix (Pearson) + covariance matrix | matrix payload for heatmap |
| Chi-Square | Independence test, e.g. payment_type × customer_segment, or category × region | `{ statistic, p_value, dof, conclusion }` |
| ANOVA | e.g. mean delivery_days across states/regions | `{ f_statistic, p_value, conclusion }` |
| T-Test | e.g. mean review_score for on-time vs. late deliveries (two-sample) | `{ t_statistic, p_value, conclusion }` |

Every statistical result returned by the API must include a `conclusion` field written in plain business language (e.g. *"Late deliveries are associated with significantly lower review scores (p < 0.001)."*) — the Analytics Dashboard renders this text next to the numbers so results are not just tables.

### 12.3 Customer Analytics (backend: `app/services/customer_analytics_service.py`)

| Feature | Definition |
|---|---|
| RFM | Recency (days since last order), Frequency (order count), Monetary (total spend) — computed per `customer_unique_id`, each binned 1–5, combined into an RFM segment label (e.g. "Champions", "At Risk", "New") |
| Customer Lifetime Value (CLV) | Historical CLV = total spend per `customer_unique_id` over observed period; documented as historical, not a forecasted CLV, to avoid overclaiming |
| Segmentation | Rule-based segments from RFM (primary) with KMeans clustering on RFM features offered as a secondary/comparison view |
| Repeat Purchase Analysis | % of `customer_unique_id`s with 2+ orders; time-between-orders distribution |
| Demographics/Regional Behaviour | Order volume, AOV, and satisfaction by state/city |

### 12.4 Business Analytics & Auto-Generated Recommendations (backend: `app/services/recommendation_service.py`)

Business analytics outputs (revenue, sales trend, product/category/seller/regional performance, payment behaviour, delivery analysis — Section 9.4) feed a **rule-based recommendation engine** (not an LLM call — deterministic, auditable rules) that evaluates conditions against the latest `marts` data and emits recommendation objects:

```json
{
  "id": "reg-underperformance-SP-2026-07",
  "category": "regional",
  "severity": "medium",
  "title": "Underperforming region: increase marketing focus",
  "description": "Region {state} grew revenue 2.1% MoM vs. a 4.8% platform average — consider reallocating marketing spend.",
  "supporting_metric": { "state": "SP", "mom_growth_pct": 2.1, "platform_avg_mom_growth_pct": 4.8 }
}
```

Minimum rule set to implement (mirrors the brief's examples): underperforming-region marketing flag, category inventory focus (top-growth category), regional delivery-performance flag (late-delivery rate above threshold), high-value-customer targeting flag (segment size + CLV threshold), satisfaction-improvement flag (region/category with review score below platform average by a significant margin, cross-checked against the T-Test/ANOVA results in 12.2 so a flag is only raised when the difference is statistically significant, not noise).

---

## 13. Machine Learning Pipeline

**Scope reminder:** exactly **one** target variable (selected per Section 5), evaluated across multiple candidate algorithms, with the winner registered and served. This is intentionally narrow — do not build multiple production models for multiple targets.

### 13.1 Pipeline Stages (`backend/app/ml/`)

| Stage | Module | Description |
|---|---|---|
| Feature building | `ml/features.py` | Builds the model-ready feature table from `curated`/`marts` for the *selected* target only, explicitly excluding any leakage columns identified in Section 5.4 |
| Preprocessing | `ml/preprocessing.py` | Encoding (one-hot/ordinal as appropriate), scaling/normalization (numeric features), train/test split (stratified) |
| Training | `ml/train.py` | Trains and compares: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost — identical train/test split and preprocessing across all five for a fair comparison |
| Evaluation | `ml/evaluate.py` | Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix, 5-fold Cross-Validation, per algorithm |
| Selection | `ml/select_model.py` | Selects best model by F1 (primary metric for imbalanced business targets) with ROC-AUC as tiebreaker; documents the choice in `ml/registry` metadata |
| Explainability | `ml/explain.py` | Feature importance (native for tree models; permutation importance for Logistic Regression) — mandatory. SHAP summary plot — optional stretch goal |
| Registration | writes to `ml.model_registry` (Section 8.4) + serializes artifact via `joblib` to `ml/registry/<model_id>.joblib` |

### 13.2 Evaluation Report Contract

`analytics/reports/model_comparison.md` must contain a single table:

| Algorithm | Accuracy | Precision | Recall | F1 | ROC-AUC | CV Mean F1 (5-fold) |
|---|---|---|---|---|---|---|
| Logistic Regression | … | … | … | … | … | … |
| Decision Tree | … | … | … | … | … | … |
| Random Forest | … | … | … | … | … | … |
| Gradient Boosting | … | … | … | … | … | … |
| XGBoost | … | … | … | … | … | … |

...followed by the selected model, its full confusion matrix, and its top-10 feature importances with a one-line business interpretation of each of the top 3.

### 13.3 Serving Contract

`POST /classification/predict` accepts a JSON body of the raw predictive features (documented per-field in the OpenAPI schema, matching exactly the feature set from `ml/features.py`) and returns:

```json
{
  "model_id": 4,
  "target_variable": "late_delivery",
  "predicted_label": "on_time",
  "predicted_probability": 0.87,
  "top_contributing_features": [
    { "feature": "seller_distance_km", "importance": 0.21 },
    { "feature": "shipping_limit_slack_days", "importance": 0.18 }
  ]
}
```

The Classification Dashboard's "single-record predict tool" (Section 10.2) is a form generated from this same feature schema, so the UI never drifts from the model's actual inputs.

---

## 14. Optional NLP Module

**This module is gated, not assumed.** Before any NLP code is written, evaluate: (a) the non-null rate of `comment_message` in `curated.reviews`, (b) the average token length of non-null comments, (c) language (expect Portuguese — flag if a translation/language-specific pipeline is required). Record this check in `analytics/reports/nlp_feasibility.md` with a clear go/no-go.

**If go:**

| Feature | Method |
|---|---|
| Sentiment Analysis | TextBlob (or a Portuguese-appropriate lexicon/model if the language check requires it) mapped against `review_score` as a sanity check |
| Keyword Extraction | Simple TF-IDF top-terms per category/segment |
| Word Cloud | Rendered from top TF-IDF terms, surfaced on the Insights Dashboard |
| Topic Modeling | LDA (via scikit-learn) with a small, fixed number of topics (e.g. 5–8), each topic hand-labeled by inspecting top terms |

**If no-go:** the Insights Dashboard's review-analytics panel falls back to `review_score` distribution and trend only (already covered by Section 12.2/9.4), and the README must state the NLP module was evaluated and skipped, with the reason.

---

## 15. Repository & Folder Structure

```
retail-bi-platform/
├── frontend/
│   ├── app/
│   │   ├── (marketing)/
│   │   ├── (auth)/
│   │   └── (app)/
│   ├── components/
│   │   ├── ui/  charts/  maps/  kpi/  filters/  layout/  recommendations/  tables/
│   ├── hooks/                     # useDashboardSummary.ts, useCustomerSegments.ts, ...
│   ├── lib/
│   │   ├── api-client/            # generated from OpenAPI schema
│   │   ├── stores/                # Zustand stores (filters, theme)
│   │   └── utils/
│   ├── styles/
│   ├── public/
│   ├── tests/                     # component + e2e tests
│   ├── .env.example
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app factory
│   │   ├── core/                  # config, security, deps
│   │   ├── db/                    # SQLAlchemy session, base
│   │   ├── models/                # ORM models (curated/marts/ml mirror Section 8)
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── routers/                # dashboard, customers, products, sellers, regions,
│   │   │                            #   payments, reviews, analytics, classification,
│   │   │                            #   recommendations, admin, auth
│   │   ├── services/                # analytics_service, stats_service,
│   │   │                            #   customer_analytics_service, recommendation_service
│   │   ├── etl/                     # ingest.py, clean.py, build_marts.py, run_all.py
│   │   └── ml/                      # features.py, preprocessing.py, train.py, evaluate.py,
│   │                                #   select_model.py, explain.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── ml/registry/                 # serialized model artifacts (.joblib) — gitignored, generated
│   ├── tests/
│   ├── .env.example
│   ├── pyproject.toml
│   └── Dockerfile
│
├── analytics/
│   ├── notebooks/
│   │   ├── 01_data_quality.ipynb
│   │   ├── 02_eda.ipynb
│   │   ├── 03_statistical_analysis.ipynb
│   │   ├── 04_target_variable_selection.ipynb
│   │   ├── 05_model_comparison.ipynb
│   │   └── 06_nlp_feasibility.ipynb        # only if Section 14 gate passes
│   └── reports/
│       ├── data_quality_report.md
│       ├── target_variable_selection.md
│       ├── model_comparison.md
│       └── nlp_feasibility.md
│
├── data/
│   ├── raw/                          # gitignored — original Kaggle CSVs
│   └── README.md                     # download instructions (dataset not committed to git)
│
├── docs/
│   ├── SRS.md                        # this document
│   ├── architecture.md
│   └── screenshots/
│
├── docker-compose.yml
├── .github/workflows/ci.yml
├── .env.example
└── README.md
```

---

## 16. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Dashboard pages must reach first meaningful paint of KPI cards in < 1.5s on a warm cache (via `marts` pre-aggregation, Section 8.1); API list/aggregate endpoints must respond in < 300ms p95 against `marts` tables |
| **Scalability** | Stateless API (horizontally scalable behind a load balancer); PostgreSQL is the only stateful component in v1 — documented as the first bottleneck to address in future scope |
| **Security** | JWT auth on all non-public routes; passwords hashed with bcrypt; parameterized queries only (SQLAlchemy ORM — no raw string-interpolated SQL); CORS restricted to the frontend origin; secrets only via environment variables, never committed |
| **Reliability** | ETL and ML training jobs are idempotent and re-runnable; `/health` endpoint checks DB connectivity |
| **Maintainability** | Strict TypeScript, typed Python (mypy-clean where practical), consistent lint/format (ESLint+Prettier, Black+Ruff), docstrings on all service functions |
| **Observability** | Structured logging (JSON logs) in the backend; request IDs propagated; basic error tracking hook point (e.g. Sentry-ready, not necessarily wired to a live account) |
| **Accessibility** | WCAG AA (Section 11.4) |
| **Internationalization** | Not required for v1 (English-only UI); currency/number formatting isolated in a single utils module so it is not a rewrite later |

---

## 17. Implementation Phases (Build Plan)

Each phase has an explicit **scope**, **deliverables**, and **exit criteria**. A phase is not "done" until its exit criteria are met — the agent should not proceed to the next phase early, and should not skip the Section 5 gate before Phase 6.

### Phase 1 — Project Setup

- **Scope:** Repository scaffolding per Section 15; Docker Compose with `frontend`, `backend`, `db` services; environment variable templates; CI skeleton (lint + build on push).
- **Deliverables:** Empty-but-runnable frontend (`/` renders) and backend (`/health` returns 200) inside Docker Compose; PostgreSQL reachable with the four schemas created (empty).
- **Exit criteria:** `docker compose up` brings up all services; CI passes on an empty commit.

### Phase 2 — Backend Foundation & ETL

- **Scope:** SQLAlchemy models + Alembic migrations for `raw`/`curated` (Section 8.2); ETL ingestion (`app/etl/ingest.py`) and cleaning (`app/etl/clean.py`); Data Quality Report generation (Section 5.2 Stage 2).
- **Deliverables:** `make etl` populates `raw` and `curated` from the downloaded CSVs; `analytics/reports/data_quality_report.md` generated.
- **Exit criteria:** Row counts in `curated` match expectations (Section 4 table, within documented dedup/cleaning deltas); report checked into the repo.

### Phase 3 — Analytics Engine & EDA/Statistics

- **Scope:** `marts` schema + batch build job (Section 8.3); EDA service + notebook (12.1); Statistics service + notebook (12.2); Customer Analytics service (12.3, RFM/CLV/segmentation).
- **Deliverables:** `analytics/notebooks/02_eda.ipynb`, `03_statistical_analysis.ipynb` completed with real output; `marts.*` tables populated.
- **Exit criteria:** All Section 12.1/12.2 required outputs present with real numbers from the actual dataset (no placeholder values).

### Phase 4 — Target Variable Selection (Gate)

- **Scope:** Execute Section 5.2 Stage 5 scoring using real Stage 3/4 outputs; write `target_variable_selection.md`.
- **Deliverables:** `analytics/reports/target_variable_selection.md` with computed scores and a stated target.
- **Exit criteria:** Report exists, is internally consistent with the EDA/stats reports, and names one (and only one) target with an operational definition and leakage-excluded feature list. **No ML code may be written before this exit criterion is met.**

### Phase 5 — API Layer

- **Scope:** All routers in Section 9.4 backed by the Phase 3 services and `marts` tables; auth (Section 9.2); shared filter param handling (Section 9.6); OpenAPI schema finalized.
- **Deliverables:** Full REST API, documented via FastAPI's auto-generated `/docs`.
- **Exit criteria:** Every endpoint in Section 9 returns real data against a seeded database; Postman/HTTP test collection or automated API tests pass.

### Phase 6 — Machine Learning

- **Scope:** Section 13 pipeline against the Phase 4 target; NLP feasibility check + optional Section 14 build.
- **Deliverables:** `analytics/reports/model_comparison.md`; registered model in `ml.model_registry`; `/classification/*` endpoints live.
- **Exit criteria:** Best model selected per the documented rule (13.1); feature importance available; `/classification/predict` returns correct-shaped responses for valid input.

### Phase 7 — Frontend & Dashboards

- **Scope:** All pages in Section 10.2; component library (10.4); design system tokens (Section 11); typed API client generated from OpenAPI; filter bar wired end-to-end; recommendations UI (12.4).
- **Deliverables:** Fully navigable app, light+dark mode, responsive at desktop/tablet/mobile breakpoints.
- **Exit criteria:** Every dashboard page renders real data end-to-end through the live API (no mock/hardcoded data remaining in components).

### Phase 8 — Testing & Hardening

- **Scope:** Section 18 test suites; accessibility pass (11.4); performance pass against Section 16 targets; security review (authz on every route, input validation).
- **Deliverables:** Test coverage report; a `docs/qa-checklist.md` sign-off.
- **Exit criteria:** CI green on lint/type-check/unit/integration/e2e; no console errors on any page; no unauthenticated access to protected routes.

### Phase 9 — Deployment & Documentation

- **Scope:** Section 19 Docker/CI-CD finalization; Section 20 README; screenshots captured into `docs/screenshots/`.
- **Deliverables:** One-command local run (`docker compose up`) from a clean clone; complete README.
- **Exit criteria:** A reviewer with no prior context can clone the repo, follow the README, and have the full app running locally, including a populated database and an active ML model, without additional undocumented steps.

---

## 18. Testing Strategy

| Layer | Tooling | Minimum Coverage |
|---|---|---|
| Backend unit | `pytest` | All service functions in Section 12 (analytics/stats/customer analytics/recommendations) and all ML pipeline stages (Section 13.1) |
| Backend integration | `pytest` + test DB (or transactional rollback fixtures) | Every router endpoint in Section 9.4, happy path + one validation-error path |
| Statistical correctness | `pytest` with known small synthetic datasets | Chi-Square/ANOVA/T-Test functions validated against hand-computed or `scipy` reference values |
| Frontend unit/component | Vitest + React Testing Library | Chart wrapper components render given typed fixture data; `FilterBar` state transitions |
| Frontend e2e | Playwright | Login → Dashboard → apply a filter → navigate to Customer Dashboard → verify data updates; Classification Dashboard predict-tool happy path |
| Type safety | `tsc --noEmit` (frontend), `mypy` (backend, best-effort) | Zero errors in CI |
| Lint | ESLint/Prettier, Ruff/Black | Zero errors in CI |

---

## 19. Deployment & DevOps

### 19.1 Docker Compose (local & reference deployment)

Services: `db` (Postgres 15, named volume for persistence), `backend` (FastAPI, depends_on `db`, runs Alembic migrations on startup), `frontend` (Next.js, depends_on `backend`). A `Makefile` at the repo root wraps common commands: `make up`, `make etl`, `make train`, `make analytics-reports`, `make test`, `make down`.

### 19.2 CI (GitHub Actions, `.github/workflows/ci.yml`)

Triggers on PR and push to `main`. Jobs: `frontend-lint-typecheck-build`, `backend-lint-typecheck-test`, `docker-build` (build both images to catch Dockerfile regressions). Merges to `main` should be blocked unless all jobs pass.

### 19.3 Environments

v1 targets a single reference environment (local Docker Compose is the primary supported deployment for the academic/portfolio context of this project). `docs/architecture.md` should include a short "Path to Production" note describing what would change for a real cloud deployment (managed Postgres, container hosting e.g. Azure Container Apps / AWS ECS given the Deloitte/Microsoft framing, secrets manager, CDN for the frontend) as documented future scope — not built in v1.

---

## 20. README Specification

The root `README.md` generated in Phase 9 must include, in this order:

1. **Project title + one-line pitch**
2. **Problem Statement** (condensed from Section 1–2)
3. **Dataset** (Section 4, with a link and a note that raw CSVs are not committed — see `data/README.md`)
4. **Architecture** (the diagram from Section 6.1, plus a one-paragraph explanation)
5. **Tech Stack** (condensed table from Section 7)
6. **Installation** (`git clone` → `.env` setup → `docker compose up` → `make etl` → `make train` → done; must actually work as written)
7. **Usage** (how to log in, how to navigate the dashboards, where the API docs live — `/docs`)
8. **Folder Structure** (condensed from Section 15)
9. **Features** (checklist mirroring Sections 9–14, checked off as actually implemented — no aspirational unchecked items presented as done)
10. **Screenshots** (placeholders referencing `docs/screenshots/*.png`, to be filled in after Phase 7)
11. **Target Variable Selection Summary** (short excerpt/link to `analytics/reports/target_variable_selection.md` — this is a notable differentiator of the project and should be visible, not buried)
12. **Future Scope** (multi-tenancy, real-time ingestion, cloud deployment per 19.3, SHAP explainability if not completed, NLP if gated out in Section 14)
13. **License / Academic Note** (state this is a final-year academic project built to production-grade engineering standards)

---

## 21. Appendix

### 21.1 Environment Variables (`*.env.example`)

**backend/.env.example**
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/retail_bi
JWT_SECRET=change-me
JWT_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:3000
ENV=development
```

**frontend/.env.example**
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### 21.2 Glossary

| Term | Meaning in this document |
|---|---|
| `curated` schema | Cleaned, deduplicated entity tables — the analytics/ML source of truth |
| `marts` | Pre-aggregated tables built specifically to serve dashboard queries fast |
| RFM | Recency, Frequency, Monetary — a customer segmentation technique |
| CLV | Customer Lifetime Value (historical, in this project — see Section 12.3) |
| Leakage | A feature that would not actually be available at prediction time (e.g. using post-delivery data to predict late delivery) |
| Gate | A phase exit criterion that must be satisfied before the next phase may begin |

### 21.3 Definition of Done (project-level)

The project is complete when: every page in Section 10.2 renders live data; the target-variable decision artifact exists and is honored by the deployed model; all statistical claims surfaced in the UI are backed by an actual computed test (Section 12.2); CI is green; `docker compose up` on a clean clone plus the documented `make` commands produces a fully working system; and the README accurately describes only what is actually built.

---

*End of document.*
