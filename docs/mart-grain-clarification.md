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

## Required correction before Phase 5

Phase 5 API implementation is gated on a mart refactor and query-plan verification:

1. Define the smallest supported filter set per endpoint before implementing its router. Unsupported filters must return Addendum v1.1's `400 / unsupported_filter`; the API must not advertise dimensions merely because the current generic mixin contains them.
2. Rebuild each primary mart at its endpoint grain, with purchase date retained only where date-range filtering or trends require it: daily revenue, date/category revenue, date/state/city regional revenue, date/seller performance, and date/payment-type mix.
3. Remove always-NULL and unrelated dimensions from each mart. Regional coordinates must be stored at one documented geographic grain rather than included as high-cardinality grouping dimensions.
4. If a business-approved endpoint genuinely requires combined filters beyond its primary grain, serve it from a separately named aggregate whose grain is explicit; do not silently turn every named summary into the same near-fact cube.
5. Rebuild from empty, reconcile every corrected mart to the shared eligible-order totals, record new row counts, add supporting indexes, and demonstrate `EXPLAIN (ANALYZE, BUFFERS)` performance before the SRS §16 API NFR is claimed.

No Phase 5 router may be implemented against the current five wide cubes. This clarification does not alter KPI definitions: delivered orders only, item price plus freight for revenue, distinct delivered orders for order count, distinct delivered customers for customer count, and purchase timestamp as the primary date axis.
