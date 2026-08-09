# Mart Refactor Validation Report

- **Generated at:** `2026-08-09T17:34:00.9607600Z`
- **Code/commit reference:** `4d6f96f4bfe5d1d61ad55459cf867992860c3392`
- **Dataset row counts used:** orders=99,441; delivered orders=96,478; order items=112,650; payment details=103,886; delivered customers=93,358
- **Authority:** Addendum v1.3 → v1.2 → v1.1 → SRS v1.0

## Final physical contracts

| Mart | Primary-key grain | Exact physical column list | Previous rows | Corrected rows | Reduction |
|---|---|---|---:|---:|---:|
| `marts.revenue_daily` | `date` | `date, revenue, order_count, customer_count, item_count` | 96,910 | 612 | 99.37% |
| `marts.revenue_by_category` | `date, category` | `date, category, revenue, order_count, customer_count, units` | 96,910 | 18,808 | 80.59% |
| `marts.revenue_by_region` | `date, state, city` | `date, state, city, revenue, order_count, customer_count, latitude, longitude` | 97,686 | 58,101 | 40.52% |
| `marts.seller_performance` | `date, seller_id` | `date, seller_id, revenue, order_count, units, avg_review_score` | 96,910 | 68,019 | 29.81% |
| `marts.payment_method_mix` | `date, payment_type` | `date, payment_type, payment_count, order_count, payment_value, avg_installments` | 68,204 | 2,247 | 96.71% |

For every table, the row count equals the distinct primary-key count; no duplicate grain exists. Regional latitude/longitude are attributes calculated as independent medians over distinct curated coordinate points per state/city and do not participate in the grain.

## Metric reconciliation

| Source / mart | Reconciled value (BRL) | Result |
|---|---:|---|
| `marts.kpi_snapshot.total_revenue` | 15,419,773.75 | Reference eligible-order revenue |
| Sum of `marts.revenue_daily.revenue` | 15,419,773.75 | Exact match |
| Sum of `marts.revenue_by_category.revenue` | 15,419,773.75 | Exact match |
| Sum of `marts.revenue_by_region.revenue` | 15,419,773.75 | Exact match |
| Sum of `marts.seller_performance.revenue` | 15,419,773.75 | Exact match |
| Sum of `marts.payment_method_mix.payment_value` | 15,422,461.77 | Exact match to delivered `curated.payment_details`; intentionally not treated as Addendum §7 revenue |

Payment value is a payment-source measure and differs from item-price-plus-freight revenue by BRL 2,688.02. The mart preserves that source fact; it does not relabel payment value as revenue.

## Migration and performance evidence

- Populated database upgraded from `e2e0c9b8f4f2` to `20260809_0002` successfully.
- Downgrade to `e2e0c9b8f4f2` and re-upgrade to `20260809_0002` both completed successfully on the populated database.
- A separate temporary database passed the supported clean sequence: create the four Phase 1 schemas, upgrade from Alembic base to head, downgrade the corrective migration, and upgrade to head again. The temporary database was removed afterward.
- A full corrected mart rebuild completed with all ten marts populated.
- The batch build runs `ANALYZE` after refresh; PostgreSQL confirms current statistics for all five tables.
- Representative post-`ANALYZE` executions for the affected marts completed below the SRS §16 300 ms API-query ceiling: daily 0.195 ms; category 3.927 ms; region 13.531 ms; seller 18.247 ms; payment 0.486 ms. These are database execution measurements, not end-to-end API latency claims.

## Phase 5 gate

The five mart schemas and build logic are clean for Phase 5 consumption at the exact grains above. The future API must accept only the filters marked supported in `docs/filter-applicability.md` and return `400 / unsupported_filter` for other shared filters. This report does not authorize or implement Phase 5.
