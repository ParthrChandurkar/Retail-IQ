# M9 Migration QA Checklist

**Status:** PASS

**Signed off:** Codex automated QA, 2026-08-26 (Asia/Calcutta)

**Scope:** final verification of the Indian Store Data migration

## Quality gates

- [x] Backend Ruff lint/format checks pass across 83 files.
- [x] Backend mypy passes across 66 source files.
- [x] Backend pytest: **41/41 tests pass**, including statistical correctness,
  seasonality regression, ML stages, filter validation, and all 27 protected
  OpenAPI operations rejecting anonymous access.
- [x] Frontend ESLint, TypeScript, Prettier, contrast checks, and production
  build pass.
- [x] Frontend Vitest/RTL: **6/6 tests pass**.
- [x] Frontend Playwright: **18/18 tests pass** across desktop, tablet, and
  mobile against the production Docker frontend.
- [x] GitHub Actions passes frontend, backend, and Docker build jobs.

The first local Playwright attempt started a second Next.js development server
after a production build and screenshot run and exhausted this Windows host's
available memory in webpack's cache. Re-running the unchanged suite against the
healthy production Docker frontend passed 18/18. This was an environmental
resource failure, not the earlier keyboard-focus flake and not an application
assertion failure.

## Live API and model verification

`python -m app.qa.endpoint_audit` independently verified **34 operations**:

- Auth: login and `/auth/me`.
- Dashboard: summary, daily/category/city-type revenue routing, categories.
- Customers: segments, cross-sectional profiles, order-value distribution,
  detail.
- Products: category/sub-category performance, categories, discount-profit.
- Regions: trusted-region sales, state choropleth, descriptive shipping.
- Analytics: correlation, hypotheses, broad screen, descriptive statistics,
  five-year seasonality.
- Classification: model info, metrics, importance, and prediction.
- Recommendations and admin: recommendations, settings GET/PUT, refresh status.
- Retired route proofs: `/sellers/*`, `/payments/*`, and `/reviews/*` all return
  **404**.

The populated project database has exactly one registered model:
`model_id=4`, target `is_high_profit_order`, algorithm Gradient Boosting,
active=true. The governed M6 request returns `high_profit_order` with confidence
`0.8327976187991819`; the value is confidence in the returned label.

## Security and accessibility

- [x] All **27 protected OpenAPI operations** return
  `401 not_authenticated` without a bearer token.
- [x] Real admin bootstrap and login were re-proved on an empty database.
- [x] Access tokens remain memory-only; rotating refresh tokens use an
  httpOnly, Secure, SameSite=Strict cookie.
- [x] `powerbi_reader` selects from `marts.kpi_snapshot` and receives
  `permission denied for schema` on `raw`, `curated`, and `ml`.
- [x] Light/dark text and chart contrast checks pass (minimum observed text
  ratio 5.98:1; dark chart series 8.03:1).
- [x] Keyboard flows and axe serious/critical checks pass at desktop, tablet,
  and mobile breakpoints. Focus outlines are not suppressed.

## Performance

Warm local production measurements against the populated marts:

| Check | Result | Target |
|---|---:|---:|
| Dashboard summary API p95, 20 samples | **117.07 ms** | <300 ms |
| Revenue-trend API p95, 20 samples | **243.98 ms** | <300 ms |
| Desktop KPI first paint | **228 ms** | <1.5 s |
| Tablet KPI first paint | **543 ms** | <1.5 s |
| Mobile KPI first paint | **402 ms** | <1.5 s |

One revenue-trend request was a 5.31 s host scheduling outlier; the governed
p95 remains 243.98 ms. The API audit's first uncached analytical report calls
are intentionally slower because they compute from curated data; dashboard
list/aggregate routes read pre-aggregated marts.

## Data, Power BI, and screenshots

- [x] Source checksum is governed in the README; ETL reconciles 100,000 raw
  rows to 100,000 orders, customers, and products.
- [x] Power BI Revenue is **₹2,50,84,41,014.18** from both
  `marts.kpi_snapshot` and `SUM(marts.revenue_daily.revenue)`.
- [x] Power BI Profit is **₹37,55,30,511.43** from both
  `marts.kpi_snapshot` and `SUM(marts.revenue_daily.total_profit)`.
- [x] Eight current screenshots were captured from authenticated, live API
  pages. The Regional screenshot shows the genuine Leaflet polygon map with 10
  populated and 19 neutral no-data states.
- [x] No unverified `.pbix` was fabricated. The environment has no controllable
  Power BI Desktop session, `pbi-tools`, Tabular Editor, or XMLA endpoint;
  `docs/powerbi-integration.md` provides a copy-paste-ready 15–20 minute path.

## Empty-database rehearsal

An isolated clone and new named volume completed the documented workflow:

1. production images built and all three services became healthy;
2. ETL loaded 100,000 raw rows and produced 100,000 curated orders;
3. all eight marts and both M3 reports/notebooks regenerated;
4. all five classifiers retrained and Gradient Boosting registered active;
5. real login, model-info, prediction, backend health, and frontend HTTP 200
   checks passed;
6. the Power BI role retained its marts-only access boundary.

GNU Make is explicitly listed as a README prerequisite but was not installed on
this Windows verification host. The rehearsal therefore invoked the exact
Docker Compose commands defined by the Makefile. No application/setup step was
added, skipped, or left undocumented.

**Admin mock note:** Playwright uses deterministic API mocks to isolate UI
behavior; real administrator seeding, login, authorization, and API data were
verified separately against both the populated project database and the clean
database rehearsal.

**Final decision:** the Indian Store Data migration is signed off against the
Migration Definition of Done.
