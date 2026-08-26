# Late-Delivery Definition Audit

> **Superseded Olist-era record.** Retained for migration history only; Delayed
> Shipment is retired from the active Indian Store Data product.

- **Generated at:** `2026-08-09T17:34:00.9607600Z`
- **Code/commit reference:** `4d6f96f4bfe5d1d61ad55459cf867992860c3392`
- **Dataset row counts used:** orders=99,441; delivered orders=96,478; delivered orders with both delivery timestamps=96,470; reviewed delivered order-links with both delivery timestamps=96,353
- **Authority:** Addendum v1.3 → v1.2 → v1.1 → SRS v1.0

## Binding definition

An order is late when:

```sql
order_delivered_customer_date > order_estimated_delivery_date
```

The comparison uses the original timestamps. It does not round or truncate the interval.

## Root cause of the discrepancy

`curated.orders.delivery_delay_days` is an integer generated with `FLOOR(EXTRACT(EPOCH FROM (delivered - estimated)) / 86400)`. It is suitable for reporting whole delay days, but `delivery_delay_days > 0` is not equivalent to the binding timestamp comparison.

| Calculation | Late orders | Denominator | Late rate |
|---|---:|---:|---:|
| Exact timestamp comparison / `curated.orders.is_late` | 7,826 | 96,470 | **8.1124%** |
| Incorrect `delivery_delay_days > 0` proxy | 6,534 | 96,470 | **6.7731%** |
| Difference | 1,292 | — | 1.3393 percentage points |

Exactly 1,292 orders arrived after the estimated timestamp but less than 24 hours late. Their floored `delivery_delay_days` is zero, which explains the entire 6.77% → 8.1124% discrepancy. The denominator is unchanged.

## Phase 3 T-test impact

No correction or rerun is required. `stats_service.t_test_review_late()` reads `curated.orders.is_late`, not `delivery_delay_days > 0`. Recalculation from the source files reproduces the checked-in Phase 3 result:

| Group | N | Mean review score |
|---|---:|---:|
| On time | 88,653 | 4.2937 |
| Late | 7,700 | 2.5665 |

- Welch statistic: `89.5507`
- p-value: below machine precision (`0.0` as emitted by SciPy)
- Conclusion: late deliveries have significantly lower review scores.

For comparison only, using the incorrect floored-day proxy would produce late `n=6,409`, on-time `n=89,944`, and `t=100.9655`. Those are not the published figures. This confirms that Phase 3 already used the correct binding label.
