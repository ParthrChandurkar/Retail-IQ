# Migration M6 Feature Contract

This contract was fixed before any migrated model-training code was written.
It implements the selected High-Profit Order target in
`analytics/reports/target_variable_selection_v2.md`.

## Complete predictive feature list

| # | Feature | Type | Availability at checkout |
|---:|---|---|---|
| 1 | `sales` | numeric | Known transaction value |
| 2 | `discount_pct` | numeric | Known applied discount |
| 3 | `category` | categorical | Known product classification |
| 4 | `sub_category` | categorical | Known product classification |
| 5 | `segment` | categorical | Known customer classification |
| 6 | `city_type` | categorical | Known customer location class |
| 7 | `state` | categorical | Known customer state |
| 8 | `region` | categorical | Trusted value joined from `curated.state_region_reference` by state |
| 9 | `order_month` | numeric | Derived from the known order date |
| 10 | `order_dow` | numeric | Derived from the known order date |

This is the full set. `quantity` is not added because it is outside the
authorized M6 list and M3 found negligible association with profit
(`r=-0.0038`). `order_year` is not added because the five annual revenue and
profit totals were effectively flat and the M6 list intentionally retains only
month/day-of-week seasonality.

## Binding exclusions

- Target/leakage: `profit`, `profit_margin_pct`, `is_high_profit_order`,
  `is_profit_outlier`, and every profit-derived flag or aggregate.
- Post-checkout: `ship_date`, `shipping_days`, and future outcomes.
- Identity/PII: order, customer, and product IDs as predictors; names, product
  name, and postal code.
- Discredited/decorative source fields: reported Region, raw Year, Ship Mode,
  Outlet Type, Country, and Postal Code. The trusted region and date-derived
  calendar fields listed above are different governed fields.

`order_id` is retained only as an audit/split-verification key and is never
passed to preprocessing or a classifier.
