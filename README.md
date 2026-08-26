# Retail IQ — Retail Business Intelligence Platform

[![CI](https://github.com/ParthrChandurkar/Retail-IQ/actions/workflows/ci.yml/badge.svg)](https://github.com/ParthrChandurkar/Retail-IQ/actions/workflows/ci.yml)
![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Next.js 14](https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs&logoColor=white)
![PostgreSQL 15](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Ready-F2C811?logo=powerbi&logoColor=111827)

**From one 100,000-row retail source to governed Indian-market KPIs,
statistical evidence, interactive dashboards, and explainable profit insight.**

## 2. 🎯 Problem Statement

Retail reporting often becomes a collection of inconsistent totals and charts
that overstate what a dataset can support. Retail IQ turns transaction data into
one governed analytics system: reproducible cleaning, shared metric definitions,
statistical tests, filter-safe marts, business recommendations, and a narrowly
scoped classifier. Analytics remains the primary product; machine learning is a
supporting decision tool.

## 3. 🗂️ Dataset

Retail IQ uses the
[Indian Store Data dataset](https://www.kaggle.com/datasets/abuhumzakhan/store-data):
**100,000 rows**, **25 source columns**, **100,000 distinct orders**, and a
five-year `order_date` range from **2019-01-01 through 2023-12-31**. It contains
customer segment/city type/state, product category/sub-category, transaction
sales/discount/profit, quantity, and shipping dates.

Raw CSV data is not committed. Follow [`data/README.md`](data/README.md) and use
the canonical local filename `data/raw/indian_store_data.csv`.

This dataset supersedes Retail IQ's earlier Brazilian Olist version. That
migration history is intentionally visible: the system was reworked when the
faculty-mandated source changed, rather than relabeling old analysis as new.
Empirical verification also found one order per Customer ID and Product ID,
making cross-sectional and category-level analytics honest choices.

## 4. 🏗️ Architecture

![Retail IQ end-to-end architecture](docs/architecture.svg)

| Stage | Responsibility |
|---|---|
| **📥 Ingest** | Load the single CSV idempotently and generate pre-clean evidence. |
| **🧹 Govern** | Normalize/validate into customers, products, orders, and trusted geography. |
| **📊 Analyze** | Build eight marts, EDA/statistics, segments, and deterministic recommendations. |
| **🧠 Model** | Compare five algorithms for the evidence-selected High-Profit Order target. |
| **🚀 Deliver** | Serve typed Next.js dashboards and read-only Power BI from the same metrics. |

PostgreSQL separates source landing (`raw`), cleaned entities (`curated`),
dashboard aggregates (`marts`), and model governance (`ml`). FastAPI owns auth,
validation, mart routing, analytics, and inference; the browser consumes its
generated OpenAPI contract. See [`docs/architecture.md`](docs/architecture.md)
for the current ER diagram, grains, trust boundaries, and production path.

## 5. 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, strict TypeScript, Tailwind CSS, React Query, Zustand, Recharts, React Leaflet, Framer Motion |
| Backend | Python 3.11, FastAPI, Pydantic 2, SQLAlchemy 2, asyncpg, Alembic |
| Analytics | pandas, SciPy, scikit-learn, Matplotlib, Seaborn, Jupyter |
| ML | Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, joblib registry |
| Data | PostgreSQL 15 with `raw`, `curated`, `marts`, and `ml` schemas |
| BI | Power BI Desktop via a marts-only database role and governed DAX |
| Quality | pytest, Ruff, mypy, Vitest/RTL, Playwright, axe-core, GitHub Actions |
| Runtime | Docker Compose and GNU Make |

## 6. 🚀 Installation

Prerequisites: Git, Docker Desktop with its Linux engine running, GNU Make, and
either Kaggle API credentials or a manually downloaded CSV. Node.js 20+ is only
needed for development/tests outside Docker. Power BI Desktop is optional for
the web app and required only to author/view a local Power BI report.

1. Clone the repository.

   ```bash
   git clone https://github.com/ParthrChandurkar/Retail-IQ.git
   cd Retail-IQ
   ```

2. Create local environment files.

   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

   PowerShell equivalents:

   ```powershell
   Copy-Item backend/.env.example backend/.env
   Copy-Item frontend/.env.example frontend/.env
   ```

   In `backend/.env`, replace `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`,
   and `POWERBI_READER_PASSWORD` with real local values. Use a valid email and
   strong unique secrets. Do not commit either `.env` file.

3. Acquire the dataset using exactly one option.

   - **Manual:** download the
     [Kaggle dataset](https://www.kaggle.com/datasets/abuhumzakhan/store-data),
     extract `store_sales_data (2).csv`, rename it to
     `indian_store_data.csv`, and place it in `data/raw/`.
   - **Automated:** export `KAGGLE_USERNAME` and `KAGGLE_KEY`, then run:

     ```bash
     make download-data
     ```

   The final payload must be `data/raw/indian_store_data.csv` (100,000 data
   rows; SHA-256 `df1dd4a0d6bd486d34499e87b249e875f2a03bc407f5ffdddddf34bea80e727e`).

4. Start PostgreSQL, FastAPI, and Next.js. Startup applies migrations and
   bootstraps the administrator from the environment.

   ```bash
   docker compose up -d
   ```

5. Ingest and clean the source.

   ```bash
   make etl
   ```

6. Build marts and regenerate EDA/statistical reports.

   ```bash
   make analytics-reports
   ```

7. Train, compare, select, and register the classifier.

   ```bash
   make train
   ```

8. Open <http://localhost:3000>, sign in with the configured administrator,
   and check API health at <http://localhost:8000/health>.

The batch workflow can take several minutes. `docker compose ps` shows service
health; `make down` stops the stack. There are no additional undocumented setup
steps.

## 7. 🧭 Usage

- Sign in at <http://localhost:3000/login>. The access token stays in memory;
  the rotating refresh token uses an httpOnly, Secure, SameSite=Strict cookie.
- Explore Executive, Sales, Customers, Products, Regional, Classification,
  Analytics, Insights, and Settings pages from the sidebar.
- Use shared date, state, city-type, category, sub-category, and segment filters;
  supported combinations are enforced by the API's mart-routing contract.
- The Regional page combines a real Indian-state choropleth with city-type
  comparison. States outside the 10 represented in the source remain neutral.
- The Classification form uses the live 10-feature schema. Output is framed as
  confidence in the returned `high_profit_order` or `standard_profit_order`
  label, never as a fixed positive-class probability.
- Swagger/OpenAPI is at <http://localhost:8000/docs>.
- Power BI setup, model relationships, DAX, and exact KPI reconciliation are in
  [`docs/powerbi-integration.md`](docs/powerbi-integration.md).
- Run `make test` for the local backend/frontend quality suite.

## 8. 📁 Folder Structure

```text
Retail-IQ/
├── frontend/               # Next.js UI, generated API client, tests
├── backend/
│   ├── app/                # API, ETL, analytics, auth, ML
│   ├── alembic/            # versioned PostgreSQL migrations
│   ├── ml/registry/        # generated joblib artifact (ignored)
│   └── tests/
├── analytics/
│   ├── notebooks/          # executable EDA/statistics artifacts
│   └── reports/            # quality, target-selection, model reports
├── data/raw/               # indian_store_data.csv (ignored)
├── docs/                   # SRS chain, architecture, routing, QA, screenshots
├── powerbi/                # governed DAX measure library
├── .github/workflows/ci.yml
├── docker-compose.yml
└── Makefile
```

## 9. ✨ Features

- [x] Single-file idempotent ingestion with generated pre/post-clean quality
  reports, normalization counts, anomaly disclosure, and retained outlier flags.
- [x] One governed INR metric dictionary for Revenue, Profit, Profit Margin,
  AOV, Average Discount, and customer/order counts.
- [x] Executive, sales, category/sub-category, cross-sectional customer,
  geographic/city-type, analytics, classification, recommendations, and admin
  APIs backed by pre-aggregated marts.
- [x] Responsive light/dark SaaS UI with server-side filters, Indian number
  grouping, accessible tables/charts, keyboard navigation, and a geographic
  React Leaflet choropleth.
- [x] EDA, broad categorical/numeric screening, correlation/covariance,
  Chi-Square, ANOVA, and T-Test results with plain-language conclusions.
- [x] Honest null-result presentation: city type does not explain profit margin
  (`p=0.5289`), and ship mode does not explain shipping duration
  (`p=0.349304`).
- [x] Category/sub-category and discount-versus-profit analysis; customer
  segment × order-value-tier × city-type comparisons.
- [x] Evidence-scored target selection, leakage exclusions, reproducible
  stratified validation, five-model comparison, labeled confusion matrix,
  global feature importance, registered artifact, and live inference.
- [x] JWT login/rotation, administrator bootstrap, protected APIs, validated
  inputs, and marts-only Power BI access.
- [x] Deterministic business recommendations backed by current mart data.
- [x] Power BI relationship guide, governed DAX library, data-quality page
  guidance, and Revenue/Profit parity proof.
- [x] CI-enforced lint, format, type-check, unit/integration/e2e, accessibility,
  production build, and Docker-image verification.

The migration deliberately removed transaction concepts absent from the new
source: payment-method, marketplace-seller, customer-review, and NLP analysis.
It also retired RFM, lifetime-value terminology, Repeat Customer Prediction,
and Delayed Shipment Classification because unique entity IDs and the measured
shipping signal cannot support those claims.

## 10. 🖼️ Screenshots

The images below are captured from the populated Indian Store Data application
in a real Chromium browser.

### Executive performance

![Executive dashboard with INR revenue and profit KPIs](docs/screenshots/executive-dashboard.png)

### Cross-sectional customer analytics

![Customer segment, order-value tier, and city-type dashboard](docs/screenshots/customer-analytics.png)

### Geographic performance

![Indian state choropleth and city-type comparison](docs/screenshots/regional-dashboard.png)

### High-Profit Order classification

![Classification metrics, importance, and prediction form](docs/screenshots/classification-dashboard.png)

### Statistical evidence

![Analytics dashboard with significant and null findings](docs/screenshots/analytics-dashboard.png)

### Recommendations

![Insights and deterministic recommendations dashboard](docs/screenshots/insights-dashboard.png)

## 11. 🧪 Target Variable Selection Summary

Retail IQ selected its migrated label only after data verification, EDA,
statistics, and feature engineering:

| Candidate | Availability | Balance | Business value | Feature support | Feasibility | Total |
|---|---:|---:|---:|---:|---:|---:|
| **High-Profit Order** | 5 | 4 | 5 | 5 | 5 | **24/25** |
| Margin Erosion | 5 | 3 | 5 | 1 | 2 | 16/25 |
| Customer Segment | 5 | 5 | 1 | 1 | 5 | 17/25 |

The selected positive class is `high_profit_order`, defined as
`profit >= ₹5,363.845` (the fixed profit P75), with 25,000 positive and 75,000
standard-profit rows. Realized profit/margin and all post-checkout fields are
excluded. The 10 permitted inputs are sales, discount, category, sub-category,
segment, city type, trusted state/region, order month, and day of week.

Gradient Boosting won by positive-class F1 (0.709218; ROC-AUC 0.923453) on the
fixed seed-42 stratified 80/20 split and is the sole active migrated model
(`model_id=4`). Read the full
[`target_variable_selection_v2.md`](analytics/reports/target_variable_selection_v2.md)
and [`model_comparison_v2.md`](analytics/reports/model_comparison_v2.md).

## 12. 🔭 Future Scope

- Multi-tenant organizations and database row-level security.
- Scheduled orchestration or CDC/stream ingestion instead of local batch jobs.
- Managed cloud PostgreSQL, container hosting, secrets manager, TLS, CDN,
  central observability, backups, and private networking.
- SHAP local explanations; the implemented model exposes governed global
  importance without fabricated local attributions.
- Author/publish a branded `.pbix` or `.pbit` through Power BI Desktop/Service;
  no unverifiable binary or Microsoft credential is committed.
- Revisit behavioral customer/product analytics only if a future source has
  genuine repeating entity IDs.
- Preserve the retired Brazilian implementation in Git history as an example of
  a governed production dataset migration.

## 13. 🎓 License / Academic Note

Retail IQ is a final-year B.Tech Data Science & Analytics project built with
production-quality engineering standards. The Kaggle dataset is governed by its
source terms and is not redistributed here. Unless a separate repository
license is added, source availability does not grant additional reuse rights.
