# Phase 3 Mart and Filter Applicability

This table is the binding Phase 3 compatibility contract for the shared filters in SRS §9.6. `date_from` and `date_to` both apply to the `date` column, which is derived exclusively from `order_purchase_timestamp` as required by Addendum §7. A mart is marked supported only when its physical DDL carries the required dimension with populated values.

| Mart / future endpoint consumer | Date | State | City | Category | Seller | Payment type | Customer segment | Review score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `kpi_snapshot` + `revenue_daily` / `GET /dashboard/summary` | Yes¹ | No | No | No | No | No | No | No |
| `revenue_daily` / `GET /dashboard/revenue-trend` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No |
| `revenue_by_category` / `GET /dashboard/top-categories`, `GET /products/categories`, `GET /products/performance` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No |
| `revenue_by_region` / `GET /regions/sales`, `GET /regions/geo` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No |
| `customer_profile` / `GET /customers/rfm`, `GET /customers/{id}`, `GET /customers/clv-distribution`, `GET /customers/repeat-purchase-rate` | No | Yes | Yes | No | No | No | Yes | No |
| `customer_segments` / `GET /customers/segments` | No | No | No | No | No | No | Yes | No |
| `seller_performance` / `GET /dashboard/top-sellers`, `GET /sellers/performance`, `GET /sellers/{id}` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No |
| `payment_method_mix` / `GET /payments/method-mix`, `GET /payments/installments-distribution` | Yes | Yes | Yes | No | No | Yes | Yes | No |
| `delivery_performance` / `GET /regions/delivery-performance` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `review_summary` / `GET /reviews/score-distribution`, `GET /reviews/trends` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

¹ `marts.kpi_snapshot` remains the required dimension-free singleton. With no date parameters, the summary reads its all-observed-period snapshot. A future summary request with `date_from` and/or `date_to` must calculate the selected and prior periods from `marts.revenue_daily`; it must not pretend that the singleton contains arbitrary period cuts. All seven non-date filters on `/dashboard/summary` remain unsupported per Addendum §6.

## Grain and metric safeguards

- The shared eligible-order definition is `order_status = 'delivered'`. Revenue is item price plus freight; AOV is delivered revenue divided by distinct delivered orders; customer count is distinct `customer_unique_id` with an eligible order.
- Revenue marts use the order's primary payment type from `curated.payment_summary`, avoiding revenue multiplication for split-payment orders.
- Customer RFM, segmentation, repeat purchase, and historical CLV read only `marts.customer_profile`. There is deliberately no `marts.customer_rfm` table.
- `marts.customer_segments` is strictly segment grain and is derived with `GROUP BY rfm_segment` over `customer_profile`.
- `review_summary` uses one deterministic row per `review_id`; delivery and review-outcome comparisons remain at order grain.
- A filter marked `No` must be rejected by the future Phase 5 API with `400` and `code: "unsupported_filter"`; Phase 3 does not add routers.
