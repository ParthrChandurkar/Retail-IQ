# Phase 3 Mart Grain Clarification

- **Reviewed at:** `2026-08-08T03:42:27.6703354Z`
- **Code/commit reference:** `3f85f4ac7ca165b7aa81ce9fde1dd57269d886d3`
- **Authority:** Addendum v1.3 → v1.2 → v1.1 → SRS v1.0

## Finding

The high and repeated row counts are a deliberate result of the Phase 3 combined-filter implementation, not a failed `GROUP BY`. The implementation used wide, pre-joined dimension cubes to satisfy Addendum v1.1 §6. However, three marts retain 96,910 rows and therefore provide little reduction from the delivered item fact population. This is a performance-design gap against the nominal SRS §8.3 grains and the SRS §16 hot-path intent, even though the rows are arithmetically aggregated and functionally filter-compatible.

| Mart | Current rows | Actual current `GROUP BY` / grain | Classification |
|---|---:|---|---|
| `marts.revenue_daily` | 96,910 | purchase date × customer state × customer city × product category × seller_id × primary payment type × customer RFM segment | Deliberate wide cube; near item grain and not genuinely daily grain |
| `marts.revenue_by_category` | 96,910 | purchase date × customer state × customer city × product category × seller_id × primary payment type × customer RFM segment | Deliberate wide cube; same physical grain as `revenue_daily`, so the table name overstates specialization |
| `marts.seller_performance` | 96,910 | purchase date × customer state × customer city × product category × seller_id × primary payment type × customer RFM segment | Deliberate wide cube; same dimensions as both revenue marts |
| `marts.payment_method_mix` | 68,204 | purchase date × customer state × customer city × payment-detail payment type × customer RFM segment | Deliberate combined-filter aggregate; category and seller columns are always NULL |
| `marts.revenue_by_region` | 97,686 | purchase date × customer state × customer city × product category × seller_id × primary payment type × customer RFM segment × customer latitude × customer longitude | Deliberate wide cube; coordinate grouping splits cities/regions further and explains the count exceeding the other three cubes |

## Completed correction before Phase 5

The corrective migration and Phase 3 build now use these physical contracts:

| Mart | Grain key (exact) | Physical columns (exact) | Supported Phase 5 filters |
|---|---|---|---|
| `marts.revenue_daily` | `date` | `date`, `revenue`, `order_count`, `customer_count`, `item_count` | date range |
| `marts.revenue_by_category` | `date, category` | `date`, `category`, `revenue`, `order_count`, `customer_count`, `units` | date range, category |
| `marts.revenue_by_region` | `date, state, city` | `date`, `state`, `city`, `revenue`, `order_count`, `customer_count`, `latitude`, `longitude` | date range, state, city |
| `marts.seller_performance` | `date, seller_id` | `date`, `seller_id`, `revenue`, `order_count`, `units`, `avg_review_score` | date range, seller_id |
| `marts.payment_method_mix` | `date, payment_type` | `date`, `payment_type`, `payment_count`, `order_count`, `payment_value`, `avg_installments` | date range, payment_type |

Regional latitude/longitude are descriptive attributes, not grain keys. Each state/city receives a stable point calculated as the independent median latitude and longitude across distinct curated customer coordinate points in that state/city; coordinates no longer split otherwise identical regional rows.

All unrelated and always-NULL dimensions have been removed. A future Phase 5 endpoint must reject every filter outside the final supported list with Addendum v1.1's `400 / unsupported_filter`. If later authority requires a combined filter not represented above, it requires a separately named aggregate with an explicit grain rather than widening these primary marts again.

This correction does not alter KPI definitions: delivered orders only, item price plus freight for revenue, distinct delivered orders for order count, distinct delivered customers for customer count, and purchase timestamp as the primary date axis.
