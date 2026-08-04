# Retail Business Intelligence Platform
## SRS Clarification Addendum v1.1

**Relationship to base document:** This addendum does **not** replace `SRS.md` v1.0. It resolves every ambiguity/inconsistency identified in the Phase-1 review (Codex, pre-implementation read-through). Wherever this document and `SRS.md` v1.0 disagree, **this document is authoritative**. It does not renumber or reorder the nine implementation phases; per the reviewer's own recommendation, this is a **Phase 0 — Clarification Sign-off** checkpoint that must be closed before Phase 1 begins.

Each item below is written as **Issue → Resolution**, with schema/DDL or policy text that can be implemented directly — no further judgment calls should be required.

---

### 1. Data-quality report sequence (Section 4.1 vs. 5.2 conflict)

**Resolution:** Split into two reports, and correct Section 5.2's stage order:

- **Stage 1 (new):** `analytics/reports/data_quality_report_pre_clean.md` — generated immediately after raw ingestion, against `raw.*`, before any cleaning logic runs.
- **Stage 2:** Cleaning, against documented thresholds (see #16 below for the outlier-handling rule).
- **Stage 2b (new):** `analytics/reports/data_quality_report_post_clean.md` — same metrics as Stage 1, plus a diff section: rows dropped, values imputed, duplicates removed, outliers flagged vs. retained, with counts and rationale for each category.

### 2. "Byte-for-byte" raw ingestion

**Resolution:** Replace with **row-and-value fidelity**: every row and column value from each CSV is loaded into `raw.*` unfiltered and untransformed, typed only as needed for storage (e.g. numeric strings → `NUMERIC`, timestamp strings → `TIMESTAMP`). No row is dropped, no value is coerced/corrected at this stage. The original CSVs in `data/raw/` remain the untouched source of truth; `raw.*` is a queryable mirror, not a literal byte copy.

### 3. Incomplete database contract — additions

`SRS.md` Section 8.2/8.3 gave a **representative subset**, not a complete contract. The following tables are now specified in full and are mandatory:

**`raw` schema** — one table per source file, 1:1 column mapping to the CSV header, all columns nullable and loosely typed (`VARCHAR`/`NUMERIC`/`TIMESTAMP` only — no constraints, so ingestion never fails on dirty source data):
`raw.customers`, `raw.orders`, `raw.order_items`, `raw.products`, `raw.sellers`, `raw.order_payments`, `raw.order_reviews`, `raw.geolocation`, `raw.product_category_translation`.

**`curated` schema — auth & admin (new):**
```sql
CREATE TABLE curated.users (
    user_id           SERIAL PRIMARY KEY,
    email              VARCHAR NOT NULL UNIQUE,
    hashed_password     VARCHAR NOT NULL,
    full_name            VARCHAR,
    role                  VARCHAR NOT NULL DEFAULT 'analyst', -- 'admin' | 'analyst' | 'viewer'
    is_active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE curated.refresh_tokens (
    token_id           SERIAL PRIMARY KEY,
    user_id              INTEGER NOT NULL REFERENCES curated.users(user_id),
    token_hash            VARCHAR NOT NULL UNIQUE,
    issued_at              TIMESTAMP NOT NULL DEFAULT now(),
    expires_at              TIMESTAMP NOT NULL,
    revoked_at              TIMESTAMP
);

CREATE TABLE curated.admin_settings (
    key         VARCHAR PRIMARY KEY,
    value        JSONB NOT NULL,
    updated_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE curated.data_refresh_log (
    id                SERIAL PRIMARY KEY,
    job_name            VARCHAR NOT NULL,   -- 'etl' | 'marts_build' | 'ml_train'
    started_at            TIMESTAMP NOT NULL,
    finished_at            TIMESTAMP,
    status                  VARCHAR NOT NULL, -- 'running' | 'success' | 'failed'
    rows_affected             INTEGER,
    error_message               TEXT
);
```
`GET /admin/data-refresh-status` (Section 9.4) reads `curated.data_refresh_log`.

### 4. `curated.customers` grain — fix, don't remove

**Issue confirmed:** `curated.customers` is correctly keyed on `customer_id` (order-linkage grain, matching the raw data's own design — one `customer_id` per order). It was mis-described as "deduplicated" — it is not, and should not be; that's the wrong table for customer-level analytics.

**Resolution:** Keep `curated.customers` exactly as specified, but re-label its purpose as *order-linkage only*. All RFM/CLV/segmentation/repeat-purchase logic (Section 12.3) reads a new **customer-grain mart** instead:

```sql
CREATE TABLE marts.customer_profile (
    customer_unique_id     VARCHAR PRIMARY KEY,
    first_order_ts            TIMESTAMP,
    last_order_ts               TIMESTAMP,
    order_count                   INTEGER,
    total_spend                     NUMERIC,     -- see #7, Revenue definition
    primary_state                     VARCHAR(2),
    primary_city                        VARCHAR,
    recency_score                         SMALLINT,
    frequency_score                         SMALLINT,
    monetary_score                            SMALLINT,
    rfm_segment                                 VARCHAR,
    clv_historical                                NUMERIC
);
```
`GET /customers/{customer_unique_id}` and all customer-analytics endpoints (Section 9.4) now read this table.

### 5. Fields lost in curation — restored

**`curated.order_items`** — add the dropped column:
```sql
ALTER TABLE curated.order_items ADD COLUMN shipping_limit_date TIMESTAMP;
```
This makes the `shipping_limit_slack_days` ML feature (Section 13.3 example) reproducible without re-deriving it from raw data at feature-build time.

**Payments** — the order-level `curated.payments` table from `SRS.md` §8.2 is renamed `curated.payment_summary` (same definition, unchanged), and a detail table is added alongside it so installment/split-payment analytics don't require going back to `raw`:
```sql
CREATE TABLE curated.payment_details (
    order_id               VARCHAR NOT NULL REFERENCES curated.orders(order_id),
    payment_sequential        INTEGER NOT NULL,
    payment_type                VARCHAR NOT NULL,
    payment_installments          INTEGER,
    payment_value                    NUMERIC NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
);
```
`curated.payment_summary` is derived from `curated.payment_details` (primary payment type = highest-value row per order; `total_payment_value` = sum). `GET /payments/installments-distribution` reads `payment_details`.

### 6. Mart/filter compatibility policy

**Resolution:** `marts.kpi_snapshot` is explicitly the **one unfiltered exception**: `GET /dashboard/summary` accepts only `date_from`/`date_to` (comparing "selected period" vs. "prior period" for the growth figures); `city`, `seller_id`, `category`, `payment_type`, `customer_segment`, and `review_score` are **not** accepted on this endpoint and must return `400 Bad Request` with `code: "unsupported_filter"` if passed. This exception is documented directly in that endpoint's OpenAPI description, not left implicit.

Every other mart listed in Section 8.3 must carry the dimension columns needed for the filters its endpoints advertise (e.g. `revenue_by_region` must include `state`/`city`; `revenue_by_category` must include `category`; both must include `date`, `payment_type` where applicable). As each mart is implemented in Phase 3, its DDL must list its dimension columns explicitly — a mart cannot be built "aggregate-only" if any endpoint reading it claims to support a filter the mart doesn't carry that dimension for.

### 7. Business metrics dictionary (binding definitions)

| Metric | Definition |
|---|---|
| **Eligible order status** | `order_status = 'delivered'` only, for every revenue/order/customer/AOV/CLV metric in the entire app. `canceled` and `unavailable` orders are excluded entirely (not counted as orders, not as cancellations-to-report — the dataset has no refund table, so this is the closest defensible proxy). In-flight statuses (`shipped`, `processing`, `invoiced`, etc.) are excluded from all revenue/analytics KPIs but may still appear in operational delivery-performance views, clearly labeled as "in-flight," not revenue. |
| **Revenue** | `SUM(order_items.price) + SUM(order_items.freight_value)` across delivered orders (i.e. total amount paid by the customer, not seller net). |
| **AOV** | Revenue ÷ delivered order count, same filter scope. |
| **Customer count** | `COUNT(DISTINCT customer_unique_id)` with ≥1 delivered order in the filtered period. |
| **Date dimension** | `order_purchase_timestamp` is the single primary axis for all filtering/trend charts app-wide (available for 100% of orders, unlike delivery dates). Delivery-specific views may additionally reference `delivered_customer_ts`, but purchase date remains the default. |
| **MoM growth** | Revenue in calendar month *M* vs. calendar month *M−1*, both by `order_purchase_timestamp`. |
| **YoY growth** | Revenue in calendar month *M* vs. the same calendar month, prior year. |
| **Refunds/cancellations** | Not modeled as a separate metric (no source data for it); handled entirely via the eligible-status exclusion above. |
| **CLV** | Historical only: `total_spend` in `marts.customer_profile` = sum of delivered-order revenue per `customer_unique_id` to date. Never presented in the UI as a forecast — label it "Lifetime Value (to date)," not "Predicted CLV." |
| **Currency** | BRL throughout, formatted `pt-BR` locale (e.g. `R$ 1.234,56`), centralized in one frontend formatting util (`lib/utils/currency.ts`) so it's a single change point. |

### 8. Authentication contract

- **Users/tokens:** see `curated.users` / `curated.refresh_tokens` DDL in #3.
- **Bootstrap:** a seed script (`backend/app/etl/seed_admin.py`) creates one admin user from `ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars on first run if `curated.users` is empty — never a hardcoded credential in source.
- **JWT claims:** `sub` (user_id), `email`, `role`, `exp`, `iat`.
- **Expiry:** access token 30 minutes; refresh token 14 days, stored hashed in `curated.refresh_tokens`, revocable via `is revoked_at IS NOT NULL`.
- **Frontend storage:** access token held in memory (React Query/Zustand auth store only, never `localStorage`); refresh token set as an `httpOnly`, `Secure`, `SameSite=Strict` cookie by the backend on login — mitigates XSS token theft. Because the refresh flow uses a cookie, `POST /auth/refresh` requires CSRF protection (double-submit token or `SameSite=Strict` alone, given this is a same-origin SPA/API pairing in v1).

### 9. Response-envelope standardization

**Binding rule:** every JSON response from `/api/v1/*` — success or error, GET or POST — includes a top-level `generated_at` (ISO-8601 UTC). This corrects the `/classification/predict` example in `SRS.md` §13.3, which is amended to:
```json
{
  "generated_at": "2018-09-12T14:03:00Z",
  "model_id": 4,
  "target_variable": "late_delivery",
  "predicted_label": "on_time",
  "predicted_probability": 0.87,
  "top_global_features": [
    { "feature": "seller_distance_km", "importance": 0.21 },
    { "feature": "shipping_limit_slack_days", "importance": 0.18 }
  ]
}
```
(Field rename explained in #10. Timestamp corrected per #15 — see below.) Error responses (`{ "detail": ..., "code": ... }`, §9.1) gain `generated_at` under the same rule.

### 10. Global vs. local explanations — resolved, not left contradictory

**Decision:** the **mandatory** deliverable is **global** feature importance only (native tree importance or permutation importance, per §13.1 — unchanged). The response field is renamed `top_contributing_features` → **`top_global_features`**, and its OpenAPI description states explicitly that these values are identical across all predictions from a given model version (they describe the model, not the record).

SHAP remains an **optional stretch goal** (§13.1, unchanged) — if and only if it is implemented, the response additionally includes a `local_shap_contributions` field (present/non-null only when SHAP is built); if not implemented, that field is simply absent. This removes the contradiction without silently forcing SHAP into scope.

### 11. Train/test strategy & temporal leakage

**New binding rule for Section 13:** the split strategy is chosen **during Phase 4**, as a required field ("Validation Strategy") in `target_variable_selection.md` — not decided upfront, and not uniform across all four candidates:

- **Outcome-at-resolution targets** (Late Delivery, Customer Satisfaction) — the label is a property of a single completed order, predicted from that same order's pre-outcome features. A stratified random train/test split is acceptable here; there is no "predict the future from the past" element to leak across.
- **Behavioral/future targets** (Repeat Customer, High-Value Customer) — these inherently require an **observation window** (e.g. a customer's first order + N months of history) and a separate **outcome window** (a following M-month period in which the label is determined). The train/test split **must** be by customer cohort/time cutoff, never a random row shuffle, or future information leaks into training. `N` and `M` must be chosen and justified in the same report field once one of these two targets is selected.

### 12. Clean-clone setup — dataset acquisition made explicit

**Resolution:** Section 20 (README) and the Phase 9 exit criteria in `SRS.md` §17 are amended. "One-command run" is corrected to **"one documented setup sequence"** — the raw dataset cannot be redistributed via Git, so a manual step is unavoidable and must be documented, not implied away:

```
1. git clone <repo>
2. cp backend/.env.example backend/.env   (and frontend/.env.example → frontend/.env)
3. Download the dataset:
   a. Manual: download from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
      and place the 9 CSVs in data/raw/, OR
   b. Automated (requires KAGGLE_USERNAME / KAGGLE_KEY env vars):
      make download-data
4. docker compose up -d
5. make etl
6. make analytics-reports
7. make train
8. Open http://localhost:3000
```
This full sequence — not an abbreviated one — is what Phase 9's exit criteria test against.

### 13. Version policy — pinned versions win

**Resolution:** explicit pinned majors in `SRS.md` §7.4 (Next.js 14, React 18, Python ≥3.11, Node ≥20 LTS, FastAPI ≥0.110, Pydantic ≥2.6, SQLAlchemy ≥2.0) are **authoritative** and override the "current stable major versions" language. That phrase is retained only for technologies with no mandated major in this document (Tailwind, shadcn/ui, Recharts, Leaflet, Framer Motion, Zustand) — for those, "latest stable at implementation time" governs.

### 14. Terminology corrections

- **Persona rename:** "Store Manager" → **"Retail Operations Manager"** throughout Section 3 and any UI copy — the dataset models marketplace sellers, not company-owned physical stores.
- **"Demographics"** (Section 12.3) is scoped strictly to **geographic + transactional-behavioral** fields (state/city, order frequency, AOV, satisfaction). No age, gender, income, or similar field exists in the dataset; none may be implied, inferred, or fabricated in any dashboard, copy, or documentation.
- **Product naming:** products have no human-readable name in the source data. All UI/API product references use `category_name_english` + `product_id` (e.g. "Health & Beauty — Product #a1b2c3d4"), never an invented product title.

### 15. Illustrative example values

All JSON payloads and numeric examples in `SRS.md` (Section 9 and elsewhere) are **contract-shape examples only** and must never be copied into real reports or seed data as if they were analytics output. The dataset's observed range is **2016–2018**; the original `/dashboard/summary` and recommendation-ID examples used a 2026 placeholder, which is corrected here — any dates appearing in real generated artifacts (reports, seeded recommendation records, demo screenshots) must fall within or immediately adjacent to 2016–2018, never a future/current-year placeholder that could be mistaken for live data.

### 16. Cleaning vs. outlier handling (supporting rule for #1)

Cleaning (Phase 2 / §5.2 Stage 2) must distinguish **invalid data** (nulls in required fields, impossible values e.g. negative price, orphaned foreign keys) from **legitimate outliers** (e.g. a genuinely high-value bulk order). Invalid data is corrected or dropped, with counts logged. Outliers are **flagged** (a boolean/indicator column, not deleted) so downstream EDA/statistics/ML can decide per-analysis whether to exclude them — deleting outliers silently at the cleaning stage is not permitted, since "high value order" is exactly the kind of row the High-Value-Customer candidate target (Section 5.3) needs to keep.

### 17. Reproducibility controls (new, minimum bar)

- Fixed random seeds for all train/test splits and any clustering (`RANDOM_SEED=42`, defined once in config, imported everywhere).
- `requirements.lock` / `poetry.lock` (backend) and `package-lock.json` (frontend) committed.
- Every generated report in `analytics/reports/` includes a header with: generation timestamp, dataset row counts used, and code/commit reference — so a report can be traced back to the exact data and code that produced it.

---

## Phase 0 — Clarification Sign-off (precedes Phase 1)

**Exit criteria:** this addendum is read and treated as binding; all seventeen items above are reflected in the Phase 1–2 scaffolding (schemas from #3–#5, `.env.example` additions for #8/#12, `Makefile` targets for #12). No phase renumbering — this is a checkpoint, not a tenth phase.

---

*This addendum is versioned independently (`v1.1`) from `SRS.md` (`v1.0`). Future clarifications should be appended here or issued as `v1.2`, etc. — the base SRS should only be edited directly for typos, never to silently absorb a scope decision.*