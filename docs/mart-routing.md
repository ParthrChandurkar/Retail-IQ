# Phase 5 Mart Routing Contract

This document is the binding router-to-mart decision table for Phase 5. It reconciles SRS §9.4 shared filters with the corrected physical grains in `docs/filter-applicability.md`. A route must never query a wider or unrelated mart merely because that table happens to contain a similarly named metric.

## Revenue routing

| Endpoint | Dimensional filters present | Mart | Query aggregation | Unsupported combinations |
|---|---|---|---|---|
| `GET /api/v1/dashboard/summary` | none | `marts.kpi_snapshot` | singleton | every non-date filter |
| `GET /api/v1/dashboard/summary` | `date_from` and/or `date_to` | `marts.revenue_daily` + eligible-order definition | selected-period revenue/orders from the daily mart; exact distinct customer count from eligible curated orders | every non-date filter |
| `GET /api/v1/dashboard/revenue-trend` | none or date only | `marts.revenue_daily` | already at date grain | — |
| `GET /api/v1/dashboard/revenue-trend` | category only, optionally with date | `marts.revenue_by_category` | sum to date grain after category predicate | category combined with state/city/seller/payment/segment/review |
| `GET /api/v1/dashboard/revenue-trend` | state and/or city only, optionally with date | `marts.revenue_by_region` | sum to date grain after geographic predicate | geography combined with category/seller/payment/segment/review; city without state |
| `GET /api/v1/dashboard/revenue-trend` | seller_id only, optionally with date | `marts.seller_performance` | sum to date grain after seller predicate | seller combined with category/geography/payment/segment/review |
| `GET /api/v1/dashboard/revenue-trend` | payment_type | none | rejected: `payment_method_mix.payment_value` is not Addendum §7 revenue | all payment-filtered revenue requests |

The revenue-trend router may therefore route to four of the five corrected marts, but it accepts at most one dimensional filter family. This preserves exact metrics without recreating a cross-dimensional fact cube.

## Fixed-domain routing

| Endpoints | Mart | Supported filters | Explicitly rejected shared filters |
|---|---|---|---|
| `GET /dashboard/top-categories`, `GET /products/categories`, `GET /products/performance` | `marts.revenue_by_category` | date range, category | state, city, seller_id, payment_type, customer_segment, review score |
| `GET /regions/sales`, `GET /regions/geo` | `marts.revenue_by_region` | date range, state, city | category, seller_id, payment_type, customer_segment, review score |
| `GET /dashboard/top-sellers`, `GET /sellers/performance`, `GET /sellers/{seller_id}` | `marts.seller_performance` | date range, seller_id | state, city, category, payment_type, customer_segment, review score |
| `GET /payments/method-mix` | `marts.payment_method_mix` | date range, payment_type | state, city, category, seller_id, customer_segment, review score |

`GET /payments/installments-distribution` is not routed through `payment_method_mix`: Addendum v1.1 §5 explicitly assigns it to `curated.payment_details`, because the corrected mart stores only average installments and cannot reproduce a distribution.

## Other endpoint sources

| Endpoint family | Authoritative source |
|---|---|
| Customer profiles/RFM/CLV/repeat rate | `marts.customer_profile`; segment summary from `marts.customer_segments` |
| Delivery performance | `marts.delivery_performance` |
| Review score distribution/trends | `marts.review_summary` |
| Product entity detail/top product IDs | curated product/order-item entities; no product-id mart exists |
| Analytics statistics | Phase 3 EDA/statistics services over curated data; fixed evidence endpoints reject shared filters, while seasonality supports date range through `revenue_daily` |
| Admin refresh status/settings | `curated.data_refresh_log`, `curated.admin_settings` |
| Recommendations | deterministic rules over corrected marts and Phase 3 statistical evidence |
| Classification | `501 Not Implemented` until Phase 6 |

## Validation rules

- `date_from <= date_to`; otherwise `422` validation error.
- `city` requires `state` so equal city names across states cannot be mixed.
- A filter unsupported by the selected route returns `400` with `code="unsupported_filter"` and a top-level UTC `generated_at`.
- `review_score_min <= review_score_max`, and each bound is within 1–5.
- All revenue paths use delivered-order item price plus freight. Payment value is never substituted for revenue.
- Customer counts are non-additive. The date-filtered summary therefore uses the shared eligible-order SQL for an exact distinct-customer count instead of incorrectly summing daily distinct counts.
- Phase 5 tests must assert the route selected for every supported revenue-trend filter family and reject every unsupported cross-family combination.
