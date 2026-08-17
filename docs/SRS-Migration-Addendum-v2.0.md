# Retail IQ — Dataset Migration Addendum v2.0
## Olist (Brazil) → Indian Store Data (India)

**Relationship to prior documents:** this is a **major-version** addendum, not a clarification. It sits **above** `SRS-Clarifications-Addendum-v1.4.md` in the authority chain and explicitly supersedes every dataset-specific section of the base SRS and prior addenda. Everything NOT called out below as superseded remains fully in force, unchanged — this is the whole point of doing this as an addendum rather than a rewrite.

**Updated authority order:**
1. **This document (v2.0)** — dataset, schema, target-selection, and metrics-dictionary authority
2. SRS-Clarifications-Addendum-v1.4.md through v1.1 — remain authoritative for everything not superseded below
3. SRS.md v1.0 — remains authoritative for architecture, frontend, auth, API conventions, testing, deployment
4. No undocumented assumptions

**What this document supersedes:** SRS §4 (Dataset Specification), §5 (target-selection *candidates* — the *process* in §5.2 is reused, not replaced), §8.2–8.4 (Database Design — curated/marts/ml schema), §12.1–12.2 (EDA/Statistics *examples* — the *module structure* is reused), §12.3 (Customer Analytics — CLV/RFM inputs), §13 (ML feature set), §14 (NLP — now formally closed as **not applicable**, not just no-go), Addendum §7 (business metrics dictionary — revenue/eligibility rules), and Addendum §21 (Power BI DAX — measures rewritten to match).

**What is explicitly NOT touched:** SRS §6 (System Architecture), §7 (Technology Stack), §9.1 (API conventions — versioning, auth header, response envelope), §10 (Frontend Architecture — routes, component library, state management), §11 (UI/UX Design System), §15 (Folder Structure — as a pattern), §16 (NFRs), §18 (Testing Strategy), §19 (Deployment/DevOps), Addendum §8 (Auth/JWT), Addendum §16–17 (outlier-handling philosophy, reproducibility controls). If a migration task seems to require touching any of these, stop and flag it — that would mean this document is wrong, not that the old constraint should be silently dropped.

**Dataset source (binding — use this exact URL, not a search result or a guess):**
`https://www.kaggle.com/datasets/abuhumzakhan/store-data`
Dataset name: **Indian Store Data**. Owner: `abuhumzakhan`. ~100,000 rows, ~20–21 columns, single flat CSV. Download via the Kaggle API (`kaggle datasets download -d abuhumzakhan/store-data`, gated behind `KAGGLE_USERNAME`/`KAGGLE_KEY` per Addendum §12's existing pattern) or manual download, placed in `data/raw/` exactly as the original dataset-acquisition flow already works — no new mechanism needed, just a new source URL and filename.

---

## 1. Dataset Comparison

| Dimension | Olist (old) | Indian Store Data (new) |
|---|---|---|
| Structure | 9 relational CSVs (customers, orders, order_items, products, sellers, payments, reviews, geolocation, category_translation) | **1 flat table**, ~100,000 rows, ~20–21 columns |
| Time range | 2016–2018 (~2 years) | 2019–2023 (~5 years) |
| Currency | BRL | INR (₹) |
| Order status | Explicit (`delivered`, `canceled`, `shipped`, ...) | **Not present** — no status/cancellation field |
| Delivery tracking | Estimated + actual delivery timestamps | **Only** Order Date and Ship Date (shipping, not delivery) |
| Reviews / ratings | `review_score` 1–5, comment text | **Absent entirely** |
| Payments | Payment type, installments, value | **Absent entirely** |
| Sellers / marketplace | Multi-seller marketplace | **No seller concept** — appears to be a single retail chain's transactions |
| Geolocation | Per-ZIP lat/lng (from a dedicated geolocation file) | **Absent** — only Postal Code / State / Region / City Type |
| Discount | Not present | **Present** (0–50%) |
| Profit | Not present (only price paid) | **Present, explicit, per line** |
| Customer segment | Derived only (RFM) | **Given directly** (Consumer / Corporate) |
| Regional granularity | State/city only | State / Region (N-S-E-W) / **City Type (Tier 1, Tier 2, Village)** — genuinely richer, and the most authentically India-specific dimension in the dataset |
| Product categories | ~71 categories (Portuguese + English translation) | **6 categories** (Furniture, Electric Appliances, Fruits & Vegetables, Household, Dairy, Fast Food) — much lower cardinality |
| PII | None (IDs + city/state only) | Customer first/last name present (synthetic data, but handle deliberately — see §4) |

**Net effect:** the project loses its entire review/satisfaction axis, its payment-behaviour axis, its seller-performance axis, and precise geolocation. It gains an explicit profit axis, a discount axis, a real customer-segment field, and a genuinely interesting India-specific regional dimension (city tier). This is a fair trade for the stated goal (Indian business context), but it is not a like-for-like swap — several modules must be **redesigned**, not just repointed.

**Unresolved facts Codex must verify empirically against the actual downloaded CSV before finalizing schema (do not assume — this mirrors the original project's own Data Quality Report discipline):**
- Whether `Order ID` repeats across multiple rows (multi-item orders, like Olist's `order_items` grain) or each row is a complete, single-item order.
- Whether `Customer ID` repeats across multiple orders at a rate sufficient for repeat-purchase/CLV/RFM analysis (this is the single most important number for salvaging the Customer Analytics module).
- The exact name of the 21st column (public description enumerates 20 explicitly; confirm the full header row).
- Exact date format/range and whether any rows have missing/null values in Ship Date, Discount, or Profit.
- Whether `Sales` is a line total (price × quantity) or a unit price, and whether `Profit` is per-line or needs recomputation.

## 2. Schema Mapping — Old Curated Entity → New Source

| Old (`curated.*`, SRS §8.2) | Status | New mapping / derivation |
|---|---|---|
| `customers` (customer_id, customer_unique_id, zip_prefix, city, state, lat, lng) | **Redesigned** | One `curated.customers` row per distinct `Customer ID` (pending the repeat-rate check above — if `Customer ID` already uniquely identifies a real person across orders, the old customer_id vs. customer_unique_id split collapses into one column, which simplifies this table). Fields: `customer_id, first_name, last_name, segment, postal_code, city_type, region, state`. No lat/lng column — see §4 for the state-centroid replacement. |
| `orders` (order_id, customer_id, order_status, purchase_ts, approved_ts, delivered_carrier_ts, delivered_customer_ts, estimated_delivery_ts, is_late, delivery_days, delivery_delay_days) | **Redesigned** | `order_id, customer_id, order_date, ship_date, ship_mode, shipping_days` (derived: `ship_date − order_date`). **No `order_status`, no `is_late`/`delivery_delay_days` in the old sense** — there is no promised/estimated date to compare against. A new `is_delayed_shipment` flag may be derived later (§8, ML updates) from a data-driven expected-shipping-duration baseline per `ship_mode`/category, **not assumed up front**. |
| `order_items` (order_id, order_item_id, product_id, seller_id, price, freight_value) | **Redesigned, pending grain check** | If multi-item orders exist: `order_id, product_id, quantity, sales, discount, profit`. If each row is already a complete order: this table collapses into `orders` directly (no separate item grain needed) — Codex decides based on the empirical check in §1, and documents which case applies. **No `seller_id`** (see below), **no `freight_value`** equivalent (no separate shipping-cost field exists — do not fabricate one). |
| `products` (product_id, category_name, category_name_english, weight/dimensions) | **Redesigned, smaller** | `product_id, product_name, category, sub_category`. No weight/dimension fields (were only used for shipping-cost/logistics context in Olist, not depended on elsewhere). |
| `sellers` | **Removed** | No seller concept in the new dataset. Every reference to seller performance (mart, endpoints, dashboard panel) is removed or reframed as *sub-category / regional* performance — see §5, §9. |
| `payment_summary` / `payment_details` | **Removed** | No payment fields at all. Every payment-method reference (mart, endpoint, Chi-Square test example, dashboard panel) is removed — see §5, §8. |
| `reviews` | **Removed** | No review data. This is the change with the largest downstream impact — see §8 (ML target re-selection, mandatory) and §9 (Insights Dashboard rework). |
| `raw.geolocation` | **Removed, replaced** | No source lat/lng data exists. Replaced with a small **static** reference table of Indian state centroids (curated by Codex from a standard public source, not derived from the dataset) — see §4. |
| `raw.product_category_translation` | **Removed** | Not needed — category names are already in one language. Optionally retained in spirit as a small `curated.categories` lookup (category + sub-category pairs) purely to drive UI filter dropdowns, not a translation table. |
| `curated.users`, `curated.refresh_tokens`, `curated.admin_settings`, `curated.data_refresh_log` | **Unchanged** | Dataset-independent. Do not touch. |
| *(new)* Discount, Profit, Segment, City Type | **New fields** | Added to `orders`/`order_items` and `customers` respectively (see above). These did not exist in any form in the old schema and are net-new analytical surface area — see §6–§9 for how they're used. |

---

## 3. Database Modifications (supersedes SRS §8.2–8.4 for this project)

**`raw` schema:** collapses from 9 tables to **1**: `raw.store_transactions`, a loose/nullable 1:1 mirror of the source CSV's actual header row (confirm all ~20–21 columns before writing the DDL — do not guess the 21st column name).

**`curated` schema — new/changed tables:**
```sql
CREATE TABLE curated.customers (
    customer_id     VARCHAR PRIMARY KEY,
    first_name       VARCHAR,
    last_name          VARCHAR,
    segment              VARCHAR NOT NULL,      -- 'Consumer' | 'Corporate'
    postal_code            VARCHAR,
    city_type                VARCHAR NOT NULL,   -- 'Tier 1' | 'Tier 2' | 'Village'
    region                     VARCHAR NOT NULL,  -- 'North' | 'South' | 'East' | 'West'
    state                       VARCHAR NOT NULL
);

CREATE TABLE curated.products (
    product_id      VARCHAR PRIMARY KEY,
    product_name      VARCHAR,
    category            VARCHAR NOT NULL,       -- 6 values, see §1
    sub_category           VARCHAR NOT NULL
);

CREATE TABLE curated.orders (
    order_id           VARCHAR PRIMARY KEY,
    customer_id           VARCHAR NOT NULL REFERENCES curated.customers(customer_id),
    order_date               DATE NOT NULL,
    ship_date                  DATE,
    ship_mode                    VARCHAR,          -- 'Standard Class' | 'Second Class' | 'First Class' | 'Same Day'
    shipping_days                  INTEGER,          -- derived: ship_date - order_date
    is_delayed_shipment               BOOLEAN          -- derived in Migration Phase M4, NOT assumed at schema-design time
);

-- Only if the multi-item-order check in §1 confirms Order ID repeats;
-- otherwise these columns fold directly into curated.orders instead.
CREATE TABLE curated.order_items (
    order_id       VARCHAR NOT NULL REFERENCES curated.orders(order_id),
    product_id       VARCHAR NOT NULL REFERENCES curated.products(product_id),
    quantity            INTEGER NOT NULL,
    sales                  NUMERIC NOT NULL,
    discount_pct              NUMERIC NOT NULL,   -- 0-50
    profit                       NUMERIC NOT NULL,
    is_price_outlier                BOOLEAN NOT NULL DEFAULT FALSE,  -- Tukey 1.5xIQR, per Addendum §16/§19 philosophy
    is_profit_outlier                  BOOLEAN NOT NULL DEFAULT FALSE
);

-- Static reference table, NOT derived from the dataset (no source lat/lng exists).
-- Populate from a standard public source of Indian state centroids; document the source.
CREATE TABLE curated.state_geocode (
    state          VARCHAR PRIMARY KEY,
    region            VARCHAR NOT NULL,
    latitude             DOUBLE PRECISION NOT NULL,
    longitude               DOUBLE PRECISION NOT NULL
);
```

**Removed entirely:** `curated.sellers`, `curated.payment_summary`, `curated.payment_details`, `curated.reviews`, and every index/FK that referenced them.

**Unchanged:** `curated.users`, `curated.refresh_tokens`, `curated.admin_settings`, `curated.data_refresh_log`, and the entire `ml` schema structure (`ml.model_registry`, `ml.predictions`, `ml.feature_importance` — table *shape* is unchanged; contents will reflect the new target once §8 is complete).

**`marts` schema — per-mart disposition:**

| Mart | Disposition | New grain |
|---|---|---|
| `revenue_daily` | Kept, extended | `date` — add `total_profit`, `total_discount_value` |
| `revenue_by_category` | Kept, recalibrated | `date, category` — only 6 categories now, table is much smaller than before; also add profit |
| `revenue_by_region` | Kept, extended | `date, state, region, city_type` — **city_type is new and should be a first-class filter**, not an afterthought |
| `seller_performance` | **Removed** | No seller concept |
| `payment_method_mix` | **Removed** | No payment data |
| `delivery_performance` | **Renamed & redefined** → `shipping_performance` | `date, ship_mode, region` — based on `shipping_days`, not delivery lateness |
| `review_summary` | **Removed** | No review data |
| `customer_profile` | Kept, enhanced | Per Addendum §4 grain (one row per real customer) — RFM/CLV computation is **more reliable now** since real `profit` is available, not just a revenue proxy. Add `segment`, `city_type` as attributes. |
| `customer_segments` | Kept | Segment-grain summary, now cross-tabbed against the *given* `segment` field (Consumer/Corporate) as well as RFM-derived segments — two independent segmentations, don't conflate them in the UI. |
| `kpi_snapshot` | Kept, extended | Add `total_profit`, `avg_discount_pct`, `profit_margin_pct` |
| *(new)* `category_discount_profit` | **New** | `category, discount_band` — supports the new discount/profit analytics surface (§6) |

## 4. Backend Changes

- **ETL (`app/etl/`):** `ingest.py` and `clean.py` rewritten for the single-flat-file source. The pre-clean/post-clean data quality report pattern (Addendum §1) is **reused as-is** — same two-report structure, same principle (flag outliers, don't delete — Addendum §16 stands unchanged), just against the new columns.
- **PII handling (new consideration, not present in the old dataset):** `first_name`/`last_name` exist now. Do not expose full customer names in any list/aggregate API response — only in the single-customer detail endpoint, and only if a page actually needs to display a name. Prefer `customer_id` + city/region in every aggregate/dashboard context, consistent with how the old dataset had no name to leak in the first place. This is a self-imposed constraint, not a source-data requirement, since the data is synthetic — but good practice costs nothing here.
- **Routers to remove:** `/sellers/*`, `/payments/*`, `/reviews/*` (all of it — not gated by feasibility this time, there is no data to feasibility-check; NLP module SRS §14 is now **formally N/A**, not NO-GO — update the language, this isn't a judgment call anymore).
- **Routers to modify:** `/regions/*` (add `city_type` filtering, drop lat/lng point-map in favor of the state-centroid choropleth), `/analytics/*` (new statistical-test pairings, §7), `/customers/*` (add `segment` as a filter/attribute), `/dashboard/summary` (new KPI fields, §9).
- **Routers to add:** `/products/discount-profit` (or fold into an existing analytics endpoint) surfacing the new discount/profit analysis.
- **Shared filter params (SRS §9.6):** drop `payment_type`, `seller_id`, `review_score_min/max`; add `city_type`, `segment`. Update `docs/mart-routing.md` and `docs/filter-applicability.md` accordingly — these documents exist specifically so this kind of change has one clear place to update, per their original purpose.
- **Business metrics dictionary (supersedes Addendum §7 for this project):**

| Metric | Old definition | New definition |
|---|---|---|
| Eligible orders | `order_status = 'delivered'` only | **All rows** — there is no status field, so no eligibility filter exists. State this explicitly in the new dictionary rather than leaving it silently absent. |
| Revenue | `SUM(price) + SUM(freight_value)` | `SUM(sales)` |
| Profit *(new)* | N/A | `SUM(profit)` |
| Profit margin *(new)* | N/A | `SUM(profit) / SUM(sales)` |
| AOV | Revenue ÷ delivered order count | `SUM(sales) ÷ COUNT(DISTINCT order_id)` |
| Customer count | Distinct `customer_unique_id` with ≥1 delivered order | Distinct `customer_id` (pending the §1 uniqueness check) |
| Date dimension | `order_purchase_timestamp` | `order_date` |
| Currency | BRL, `pt-BR` formatting | **INR, `en-IN` formatting** (₹1,23,456.78 — Indian digit grouping, not Western) |
| Avg. discount *(new)* | N/A | `AVG(discount_pct)` |

## 5. EDA Updates (supersedes SRS §12.1 examples; module structure unchanged)

| Analysis | Old example | New example |
|---|---|---|
| Univariate | Distribution of price, freight, delivery_days, review_score | Distribution of **sales, discount_pct, profit, shipping_days** |
| Bivariate | Price vs. freight scatter; review_score vs. delivery_delay boxplot | **Discount vs. profit scatter** (does higher discount erode profit, and how much); **shipping_days by ship_mode boxplot** |
| Multivariate | Correlation matrix across order/delivery/payment features | Correlation matrix across **sales, discount_pct, profit, quantity, shipping_days** |
| Trend | Monthly revenue/orders | Monthly revenue/orders/profit — now over **5 years instead of 2**, genuinely supports seasonality analysis better than before |

## 6. Feature Engineering Updates

New derived features that didn't exist before: `profit_margin_pct` (row-level), `discount_band` (e.g. none/low/medium/high, thresholds set from the data's actual distribution, not assumed round numbers), `shipping_days`, `is_delayed_shipment` (data-driven baseline per `ship_mode`, derived in Migration Phase M4 — not before), `is_repeat_customer` (pending the §1 uniqueness check), `order_month`/`order_year`/`order_dow` for seasonality. Removed: everything derived from `freight_value`, `payment_installments`, `review_score`, `seller_id`.

## 7. Statistical Analysis Updates (supersedes SRS §12.2 examples; module structure unchanged)

The three-test requirement (one Chi-Square, one ANOVA, one T-Test, each with statistic/p-value/plain-language conclusion) stands unchanged. New pairings, since the old ones depended on removed fields:

| Test | Old example (now impossible) | New example |
|---|---|---|
| Chi-Square | Payment method × customer segment | **`category` × `segment`** (is product-category preference associated with Consumer vs. Corporate buyers?) |
| ANOVA | Mean delivery duration across states | **Mean `shipping_days` across regions**, or mean `profit_margin_pct` across `city_type` |
| T-Test | Review score: late vs. on-time delivery | **Mean `profit_margin_pct`: high-discount vs. low-discount orders** (does discounting meaningfully erode margin, or is it statistically noise) — this is arguably a *more* business-relevant test than the one it replaces |


## 8. Machine Learning Target Updates — MANDATORY RE-SELECTION (supersedes SRS §5 candidates; the §5.2 *process* and the Addendum §22 *principle* both carry forward unchanged)

**This is the most important constraint in this entire document.** The currently-registered model predicts Customer Satisfaction from `review_score`. That field no longer exists anywhere in the data. **The existing model, its target, and its `target_variable_selection.md` are retired, not adapted.** A new target must be selected through the exact same staged, scored process as the original Phase 4 — cleaning → EDA → statistics → candidate scoring → documented selection — **before any new training code is written.** Skipping straight to "the obviously similar target" is exactly the shortcut the original project was built to prevent, and it applies with full force here.

**New candidate targets** (replacing the four in SRS §5.3 — score all five for real, against the real cleaned data, using the identical 1–5 rubric across Data Availability, Class Balance, Business Value, Feature Support, and Feasibility):

| Candidate | Definition | Notes for scoring |
|---|---|---|
| **High-Profit Order/Customer Classification** | Predict whether an order (or a customer's aggregate behaviour) falls in the top X% by profit | Directly backed by real `profit` data — arguably a stronger foundation than the old High-Value-Customer candidate ever had, since that one relied on a revenue proxy |
| **Repeat Customer Prediction** | Will a customer place a second order within N months | Only viable if the §1 uniqueness check shows a meaningful repeat rate — could be a non-starter, same risk profile as before |
| **Delayed Shipment Classification** | `shipping_days` exceeding a data-driven baseline (§6) | Closest available proxy to the old Late Delivery candidate; **must not use `ship_date` itself as a predictive feature** — that's the leakage-equivalent of using the outcome to predict itself |
| **High-Discount / Margin-Erosion Classification** | Predict whether an order will be both high-discount and low-margin | New; check for leakage carefully — if `profit`/`sales` are already discount-adjusted, using them to predict discount level is circular |
| **Customer Segment Classification** | Predict Consumer vs. Corporate | Include for rigor, but likely to score low on Business Value — `segment` is typically already known at transaction time, so "predicting" it has limited operational use. Score it honestly rather than dropping it, so the final report shows the full comparison, not a pre-narrowed one. |

**Validation strategy (Addendum §11 principle, reapplied):** outcome-at-resolution candidates (High-Profit Order, Delayed Shipment, High-Discount/Margin, Segment) may use a stratified random split. The one behavioural/future candidate (Repeat Customer) requires the same observation-window/outcome-window/cohort-split treatment as before — do not default to a random split for it.

**Positive class & metric convention (Addendum §22 principle, reapplied — the specific label names do not carry forward):** whichever target is selected, define the positive class as the business-actionable one (the outcome worth flagging/acting on), not the majority class, and state it explicitly with the same reasoning discipline as Addendum §22. Report Precision/Recall/F1 for that class specifically. Define new `predicted_label` string values appropriate to the new target (not `low_satisfaction`/`high_satisfaction` — those are retired).

**Deliverable:** a new `analytics/reports/target_variable_selection_v2.md` (the original is renamed `target_variable_selection_olist_v1.md` and kept for history — this project's own migration story is worth being able to show, not deleted). No model-training code exists until this file is committed with real, computed scores.

**NLP (SRS §14):** now formally **Not Applicable**, not a NO-GO — there is no review or free-text field of any kind in the new dataset, so there is nothing to feasibility-check. Update every reference (README, architecture doc, Insights Dashboard) to say N/A, not "evaluated and declined."

## 9. Dashboard KPI Updates

| Page | Removed | Added / Changed |
|---|---|---|
| Dashboard (home) | Customer Satisfaction KPI | **Total Profit, Profit Margin %, Avg. Discount %** added to the KPI strip alongside Revenue/Orders/Customers/AOV |
| Sales Dashboard | — | Profit trend alongside revenue trend; category breakdown now spans only 6 categories, so surface **sub-category** more prominently to keep the view informative |
| Customer Dashboard | — | RFM/CLV kept and strengthened (real profit, not a proxy); add a Consumer-vs-Corporate cut alongside the RFM segments — keep these two segmentations visually distinct, don't merge them |
| Product Dashboard | Seller performance | Discount vs. profit view added (the new EDA bivariate analysis surfaced directly, not just buried in a report) |
| Regional Dashboard | Precise point map (no lat/lng source) | **State-centroid choropleth** using `curated.state_geocode`; **City Type (Tier 1/2/Village)** as a first-class comparison — this is the dataset's standout India-specific dimension and deserves a dedicated view, not just a filter |
| Classification Dashboard | Old predict-tool fields (review-era feature set) | New predict-tool form matching whatever target is selected in §8; confusion matrix / feature importance regenerated against the new model |
| Analytics Dashboard | Payment-method Chi-Square example | New test pairings per §7 |
| Insights Dashboard | Review-score distribution/trend, NLP fallback language | Discount/margin insights; recommendation panel using the reworked rule set below |
| Settings | — | Unchanged |

**Business recommendation rules (SRS §12.4 — same five-rule structure, one rule swapped):** regional underperformance, category growth focus, and high-value/high-profit-customer targeting carry forward with updated field references. The delivery-performance flag is renamed to a shipping-performance flag (based on `shipping_days`, not delivery lateness). The satisfaction-improvement flag — which depended on review scores and was cross-checked against the old T-test — is **retired** and replaced with a **discount-margin-erosion flag**: categories or regions where heavy discounting is statistically associated with reduced profit margin, cross-checked against the new T-test in §7, exactly the same "only fire on statistically significant findings" discipline as before.

## 10. Power BI Dashboard Modifications

- **DAX measure library** (`powerbi/RetailIQ-Measures.dax`) rewritten to match the §4 metrics dictionary exactly: `Revenue = SUM(sales)`, new `Total Profit`, `Profit Margin %`, `Avg Discount %` measures. Remove any measure referencing payment type, seller, or review score.
- **Relationships/data model** simplified — far fewer tables now (no seller/payment/review tables to relate), document the new, smaller relationship diagram in `docs/powerbi-integration.md`.
- **Reconciliation check** (same discipline as before): after the rebuild, Power BI's Revenue and Profit figures must exactly match the live dashboard's — verify and state the numbers, the way the original migration verified Revenue to the cent.
- The `powerbi_reader` role/grant pattern itself (Addendum v1.3 §21.2) is unchanged — same least-privilege boundary, just against the new (smaller) `marts` schema.

## 11. Documentation Updates

- `docs/architecture.md`: dataset section rewritten; the old 9-table hub-and-spoke ERD is replaced with the new, much simpler schema diagram (§3).
- `docs/qa-checklist.md`: cannot simply be re-signed — nearly every layer changed. Re-run the full Phase 8 test suite against the new schema/API/model and re-sign for real, not by inheritance.
- `docs/mart-routing.md`, `docs/filter-applicability.md`: updated per §4's filter-parameter changes.
- `docs/screenshots/*.png`: **must be recaptured**. The old screenshots show BRL currency, Olist categories, and review-based panels that no longer exist — keeping them would make the README actively misleading, not just outdated.

## 12. README Updates

- **Dataset section**: fully rewritten — name, Kaggle URL (`https://www.kaggle.com/datasets/abuhumzakhan/store-data`), row count, date range, column summary, and an honest one-line note that this supersedes an earlier Brazilian-dataset version (worth keeping as a visible fact, not hiding it — migrating a production system to a new data source under a faculty constraint is itself a legitimate engineering story, not something to erase from the record).
- **Target-variable-selection summary**: rewritten once §8 completes, pointing at `target_variable_selection_v2.md`.
- **Features checklist**: re-verified line by line — payment/seller/review/NLP items removed or marked N/A; discount/profit/city-tier items added.
- **Installation**: dataset-acquisition step (Addendum §12) updated to the new Kaggle URL and filename(s).
- **Future Scope**: may note the retired Brazilian-dataset version is preserved in git history/a tag, for anyone who wants to see the earlier iteration.

---

## Execution Order (Migration Phases M1–M9)

Same discipline as the original nine-phase build: work through these in order, report back with real evidence at each step, and continue phase-by-phase authorization unless you'd rather hand the whole thing over at once — the phase-gate pattern is what caught every real defect in the original build, so continuing it is the default recommendation, not a requirement I'm imposing without reason.

1. **M1** — Dataset acquisition, empirical verification of the open questions in §1, raw/curated schema migration, ETL rewrite, pre/post-clean quality reports.
2. **M2** — Marts rebuild (§3), `mart-routing.md`/`filter-applicability.md` updated.
3. **M3** — EDA & Statistics rework (§5, §7), new notebooks/reports.
4. **M4** — Feature engineering (§6), including the data-driven delayed-shipment baseline.
5. **M5** — **Target re-selection (§8) — gated.** No ML code before `target_variable_selection_v2.md` exists.
6. **M6** — API layer updates (§4 routers), Power BI role/grants re-verified against the new schema.
7. **M7** — ML pipeline rebuilt against the new target (SRS §13 process, Addendum §22 principle).
8. **M8** — Frontend updates (§9): remove dead UI, add new panels, currency formatting switched to `en-IN`/₹.
9. **M9** — Power BI docs/DAX (§10), full documentation/README pass (§11–12), full re-verification (re-run the entire Phase 8 QA suite — do not inherit the old sign-off), screenshots recaptured.

## Migration Definition of Done

The migration is complete when: every dashboard page renders live data from the Indian Store Data schema with no leftover references to reviews, payments, or sellers; a new classification target has been selected through the full scored process in §8 and is honored by a newly trained, newly registered model; every statistical claim in the UI is backed by a real computed test against the new data; Power BI's Revenue and Profit reconcile exactly to the live dashboard; CI is green end-to-end; a clean clone plus the documented setup produces a fully working system pointed at the new dataset; and the README accurately describes only what is actually built — including, honestly, what was removed and why.
