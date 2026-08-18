# Migration M2 Mart and Filter Applicability

This is the physical filter contract for the Indian Store Data marts. `date` is derived exclusively from `curated.orders.order_date`; geographic `region` is derived exclusively from `curated.state_region_reference`, never from `customers.region_as_reported`.

| Mart | Date | Region | State | City type | Category | Sub-category | Segment | Ship mode | Order-value tier | Discount band |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `kpi_snapshot` | No¹ | No | No | No | No | No | No | No | No | No |
| `revenue_daily` | Yes | No | No | No | No | No | No | No | No | No |
| `revenue_by_category` | Yes | No | No | No | Yes | Yes | No | No | No | No |
| `revenue_by_region` | Yes | Yes | Yes | Yes | No | No | No | No | No | No |
| `shipping_performance` | Yes | Yes | No | No | No | No | No | Yes | No | No |
| `customer_profile` | Yes² | Yes | Yes | Yes | No | No | Yes | No | Yes | No |
| `customer_segments` | No | No | No | Yes | No | No | Yes | No | Yes | No |
| `category_discount_profit` | No | No | No | No | Yes | Yes | No | No | No | Yes |

¹ `kpi_snapshot` is the dimension-free, all-observed-period singleton. Date-filtered KPI requests use `revenue_daily`.

² `customer_profile.order_date` supports cross-sectional cohort filtering. It is not repeat-purchase history.

## Grain and integrity safeguards

- All curated orders are eligible because the source has no status/cancellation field.
- Revenue is `SUM(sales)`; profit is `SUM(profit)`; AOV is revenue divided by distinct orders; customer count is distinct `customer_id`.
- `revenue_by_category` grain is `date × category × sub_category`; no Product-ID aggregation is exposed because Product ID repetition is 0%.
- `revenue_by_region` grain is `date × state × region × city_type`, with region obtained from the trusted state mapping.
- `customer_profile` is cross-sectional. It contains Order Value, never CLV, and contains no Frequency or monetary-over-time score.
- `customer_segments` is `segment × order_value_tier × city_type`, using data-derived order-value quartiles.
- Discount bands are data-derived quartiles rather than assumed round-number thresholds.
- `shipping_performance` is descriptive only. M2 found ship-mode durations effectively indistinguishable, so it must not be interpreted as proof of service-level performance or used as a delayed-shipment label.
- Removed marts: `seller_performance`, `payment_method_mix`, `review_summary`, and `delivery_performance`.
