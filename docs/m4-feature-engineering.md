# Migration M4 Feature Engineering Contract

Generated: 2026-08-19 (Asia/Calcutta)

## Shipping-days gate

`shipping_days` has no defensible predictor in the M3 evidence:

- Ship Mode × shipping days: ANOVA p=0.349304, η²=0.0000329; Kruskal–Wallis p=0.348238.
- Every Ship Mode has median shipping duration 4 days; mode means span only 3.973340–4.002843 days.
- Pearson correlations with Sales, Profit, Discount, Quantity, and Profit Margin range from −0.002603 to 0.004981 in absolute magnitude.
- No categorical grouping in the 78-pair M3 screen produced a material shipping-days effect after FDR correction.

**Decision:** do not create `is_delayed_shipment`. There is no evidence-backed expected-duration baseline and therefore no defensible positive class. The Delayed Shipment candidate should be treated as infeasible entering M5, not scored as if a valid target existed. The nullable schema placeholder was removed in migration `20260819_0008`.

## Canonical row-level features

All thresholds are recomputed from the cleaned order population; none is hardcoded from the current CSV values.

| Feature | Canonical definition | Current-data evidence | Lineage |
|---|---|---|---|
| `profit_margin_pct` | `100 × profit / sales` | zero nulls; maximum stored-vs-formula delta 0 | M3-confirmed Sales and Profit |
| `discount_band` | Data-derived Discount quartiles, with Q1 owned by `low` and Q3 owned by `high` | Q1=13%, median=25%, Q3=38% | M3-confirmed Discount |
| `is_high_profit_order` | `profit >= P75(profit)` | P75=₹5,363.845; 25,000 positive rows | M3-confirmed Profit |
| `order_month` | Month 1–12 from `order_date` | zero derivation mismatches | Confirmed Order Date |
| `order_year` | Four-digit year from `order_date` | 2019–2023; zero derivation mismatches | Confirmed Order Date, never raw `Year` |
| `order_dow` | ISO weekday 1=Monday through 7=Sunday from `order_date` | zero derivation mismatches | Confirmed Order Date |

### Canonical discount bands

| Band | Boundary rule | Current range | Rows |
|---|---|---:|---:|
| `low` | `discount_pct <= Q1` | 0–13% | 26,706 |
| `medium_low` | `Q1 < discount_pct < median` | 14–24% | 21,883 |
| `medium_high` | `median <= discount_pct < Q3` | 25–37% | 26,130 |
| `high` | `discount_pct >= Q3` | 38–50% | 25,281 |

This definition is generated once during curated cleaning and persisted on `curated.orders`. The `category_discount_profit` mart groups the stored value, and the discount-margin T-test selects stored `low` and `high` bands. Neither consumer recalculates competing boundaries.

## Explicit exclusions

- No `is_repeat_customer`: 0/100,000 customers repeat.
- No Product-ID-grained feature: 0/100,000 Product IDs repeat.
- No feature uses `region_as_reported`, raw `Year`, Ship Mode, Outlet Type, Country, or Postal Code as a predictor.
- Trusted Region remains a valid descriptive geography but is not used to manufacture any M4 target.
