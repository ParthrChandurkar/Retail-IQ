# Phase 8 QA Checklist

**Status:** PASS

**Signed off:** Codex automated QA, 2026-08-12 (Asia/Calcutta)

**Scope:** SRS §17 Phase 8 and §18 only; no Phase 9 deliverables are present.

## Test-suite sign-off

- [x] Backend lint, formatting, strict mypy, and 35 pytest tests pass.
- [x] Backend service and ML stages cover filters/pagination, security primitives, mart routing, ETL contracts, feature leakage, group-aware split, preprocessing, evaluation semantics, model selection, classification confidence, and Phase 3 analytics/statistics.
- [x] Statistical correctness is checked against synthetic known values for Chi-Square, ANOVA, and independent T-Test in `backend/tests/test_phase3_analytics.py`.
- [x] Seasonality SQL regression test proves the filter clause is interpolated and parameterized; literal `{where}` cannot recur unnoticed.
- [x] Frontend lint, type-check, contrast automation, Vitest/RTL (5 tests), production build, and Playwright (12 tests) pass.
- [x] Playwright covers login → dashboard → category-filter routing → customer navigation and classification prediction in desktop, tablet, and mobile viewports.
- [x] Browser console/page-error collection passes with no errors; the missing favicon that caused the only observed 404 was fixed with `frontend/app/icon.svg`.

## Independent API verification

`python -m app.qa.endpoint_audit` verified **39/39 operations** individually against the populated Docker stack. Every operation returned its expected 200 response:

- Auth: login, refresh rotation, me.
- Dashboard: summary, revenue trend, top categories, top sellers, top products.
- Customers: segments, RFM, CLV distribution, repeat purchase, detail.
- Products: performance, categories, detail.
- Sellers: performance, detail.
- Regions: sales, geo, delivery performance.
- Payments: method mix, installment distribution.
- Reviews: score distribution, trends, NLP no-go fallback summary.
- Analytics: correlation/covariance, hypothesis tests, descriptive statistics, seasonality.
- Classification: model info, metrics, feature importance, predict.
- Recommendations and admin: recommendations, settings GET/PUT, refresh status.

Validation-error coverage includes malformed login and prediction bodies, malformed settings PUT, invalid pagination, and invalid shared-filter ranges. Detail endpoints also retain explicit 404 tests through their service/router contracts.

## Security sign-off

- [x] All **36 protected operations** were enumerated from OpenAPI and returned `401 not_authenticated` without a bearer token.
- [x] Auth uses memory-only access tokens; refresh stays in an httpOnly, Secure, SameSite=Strict cookie.
- [x] API SQL filter values remain positional parameters, with regression coverage.
- [x] Power BI least privilege was re-proved after Phases 6–7:

| Probe executed after `SET ROLE powerbi_reader` | Result |
|---|---|
| `SELECT count(*) FROM marts.kpi_snapshot` | PASS (1 row) |
| `SELECT count(*) FROM raw.orders` | DENIED: permission denied for schema raw |
| `SELECT count(*) FROM curated.orders` | DENIED: permission denied for schema curated |
| `SELECT count(*) FROM ml.model_registry` | DENIED: permission denied for schema ml |

- [x] Dependency review completed. Python checks are clean. `npm audit --omit=dev` reports two high advisories in the SRS-bound Next.js 14/PostCSS chain; the automated fix requires the undocumented breaking move to Next.js 16, so this is recorded as a governed Phase 9/maintenance upgrade rather than violating the specified stack in Phase 8.

## Accessibility sign-off

- [x] Light/dark token contrast: body text ≥ 5.98:1; dark chart series ≥ 8.03:1.
- [x] Keyboard-only login, filter, sidebar/mobile navigation, and prediction controls pass.
- [x] Native focus rings remain visible; no CSS rule suppresses outlines.
- [x] Axe finds zero serious/critical violations on the authenticated dashboard across desktop, tablet, and mobile.
- [x] Loading/error/prediction states use appropriate `role="alert"` or `aria-live` announcements.

## Performance sign-off

Measured locally against populated Postgres 15 marts after one warm-up request, 20 samples per endpoint. SRS target: API p95 <300 ms.

| Endpoint | Warm p95 |
|---|---:|
| Dashboard summary | 108.54 ms |
| Revenue trend | 126.58 ms |
| Top categories | 111.54 ms |
| Top sellers | 206.46 ms |
| Customer segments | 93.57 ms |
| Customer RFM | 215.71 ms |
| CLV distribution | 291.62 ms |
| Repeat purchase | 119.40 ms |
| Product performance | 107.43 ms |
| Seller performance | 263.71 ms |
| Region sales | 137.34 ms |
| Region geo | 233.34 ms |
| Delivery performance | 279.49 ms |
| Payment mix | 130.76 ms |
| Review distribution | 148.85 ms |
| Review trends | 170.53 ms |
| Seasonality | 94.05 ms |

CLV distribution initially measured 342.34 ms p95. Migration `20260812_0005` adds a CLV index, reducing the measured p95 to 291.62 ms. Dashboard KPI rendering was decoupled from slower supporting charts. Warm KPI first-paint evidence from Playwright: desktop **137 ms**, tablet **1,037 ms**, mobile **1,085 ms**, all below the 1.5-second target.

## Defects found and resolved

1. Added a seasonality regression test for the previously fixed literal `{where}` query defect; no further endpoint used that pattern.
2. CLV distribution exceeded the API p95 NFR; added a governed index migration and re-measured below target.
3. Executive KPI first paint waited for every chart query; made supporting panels independently progressive so KPI readiness controls first paint.
4. Public login triggered an unnecessary refresh request, producing an expected 401 console error; refresh is now attempted only on protected routes.
5. Browser audit found a favicon 404; added the application icon and re-verified a clean console.

## Phase 9 deployment verification

- [x] Rehearsed the documented sequence against a new Compose project and an
  empty PostgreSQL volume: migrations, admin bootstrap, nine-file ETL, marts,
  reports, model training/registration, and all services completed successfully.
- [x] The populated rehearsal verified 39 API operations, backend and frontend
  health, and a registered Logistic Regression model (`model_id = 1`).
- [x] The Power BI login selected from `marts.kpi_snapshot` and was denied access
  to `raw`, `curated`, and `ml`.
- [x] Power BI reconciliation was exact: Revenue **R$ 15,419,773.75** and AOV
  **R$ 159.8268387611683493** matched `marts.kpi_snapshot` and the governed
  `revenue_daily` calculation.
- [x] A 512 MB PostgreSQL shared-memory allocation is declared in Compose; this
  resolves the clean-clone model-training failure observed with Docker's default
  64 MB `/dev/shm` allocation.
- [x] Final production images build, `GET /health` returns 200, the frontend root
  returns 200, and the complete local quality suite passes.

**Final decision:** Phase 8 and Phase 9 verification criteria are signed off.
