# Data Quality Report — Pre-Clean

- **Generated at:** `2026-08-17T11:53:16.517276+00:00`
- **Code/commit reference:** `18eb91c50260b131d20baa6fe04d36db493fe2ee`
- **Dataset row counts used:** store_transactions=100,000

## Source structure

| Check | Result |
|---|---:|
| Rows | 100,000 |
| Columns | 25 |
| Advertised columns | 20–21 |
| Actual 21st column | `Sub-Category` |
| Exact duplicate rows | 0 |

## Empirical grain verification

| Question | Result |
|---|---|
| Repeated Order IDs | **No** (0 duplicate rows) |
| Repeated Customer IDs | **No** (0 duplicate rows) |
| Multi-item orders | **0**; each order occupies exactly one source row |
| Repeat customers | **0 / 100,000 (0.0000%)** |

## Date coverage

| Field | Minimum | Maximum | Nulls |
|---|---|---|---:|
| Order Date | 2019-01-01 | 2023-12-31 | 0 |
| Ship Date | 2019-01-02 | 2024-01-07 | 0 |
| Sales Date | 2019-01-01 | 2023-12-31 | 0 |

### Source date consistency

| Check | Mismatched rows | Mismatch rate |
|---|---:|---:|
| `Year` vs Sales Date year | 79,888 | 79.8880% |
| `Year` vs Order Date year | 80,023 | 80.0230% |

The independently generated `Year` and `Sales Date` fields are retained in raw for auditability but are not used to overwrite the binding `Order Date`.

## Column null rates

| Column | Null count | Null percentage |
|---|---:|---:|
| `raw.store_transactions.customer_id` | 0 | 0.0000% |
| `raw.store_transactions.customer_name` | 0 | 0.0000% |
| `raw.store_transactions.last_name` | 0 | 0.0000% |
| `raw.store_transactions.date_of_birth` | 0 | 0.0000% |
| `raw.store_transactions.sales` | 0 | 0.0000% |
| `raw.store_transactions.year` | 0 | 0.0000% |
| `raw.store_transactions.outlet_type` | 0 | 0.0000% |
| `raw.store_transactions.city_type` | 0 | 0.0000% |
| `raw.store_transactions.category_of_goods` | 0 | 0.0000% |
| `raw.store_transactions.region` | 0 | 0.0000% |
| `raw.store_transactions.country` | 0 | 0.0000% |
| `raw.store_transactions.segment` | 0 | 0.0000% |
| `raw.store_transactions.sales_date` | 0 | 0.0000% |
| `raw.store_transactions.order_id` | 0 | 0.0000% |
| `raw.store_transactions.order_date` | 0 | 0.0000% |
| `raw.store_transactions.ship_date` | 0 | 0.0000% |
| `raw.store_transactions.ship_mode` | 0 | 0.0000% |
| `raw.store_transactions.state` | 0 | 0.0000% |
| `raw.store_transactions.postal_code` | 0 | 0.0000% |
| `raw.store_transactions.product_id` | 0 | 0.0000% |
| `raw.store_transactions.sub_category` | 0 | 0.0000% |
| `raw.store_transactions.product_name` | 0 | 0.0000% |
| `raw.store_transactions.quantity` | 0 | 0.0000% |
| `raw.store_transactions.discount` | 0 | 0.0000% |
| `raw.store_transactions.profit` | 0 | 0.0000% |

## Financial semantics

Kaggle defines `Sales` as the purchase amount in INR and `Profit` as profit calculated after applying discount. Since every Order ID has exactly one row, both values are complete transaction-line amounts; `Sales` is not a unit price and `Profit` requires no aggregation or recomputation before curation.

- Quantity/Sales correlation: **-0.002201**; Sales was generated independently of quantity, so a unit price cannot be recovered by treating Sales as price-per-unit.
- Quantity range: **1–10**.
- Discount range: **0.00–0.50** in the source (0%–50%).
- Ship Date null rate: **0.0000%**.
- Discount null rate: **0.0000%**.
- Profit null rate: **0.0000%**.

## Global Tukey outlier candidates

Outliers are candidates for flags only and are not deleted.

| Field | Q1 | Q3 | IQR | Lower | Upper | Flagged | Flagged % |
|---|---:|---:|---:|---:|---:|---:|---:|
| `sales` | 12618.0300 | 37575.8500 | 24957.8200 | -24818.7000 | 75012.5800 | 0 | 0.0000% |
| `profit` | 1651.1050 | 5363.8450 | 3712.7400 | -3918.0050 | 10932.9550 | 1,213 | 1.2130% |

## Geographic integrity anomaly

All **10 of 10 states** occur under all **4** reported regions. `State → Region` is therefore not a valid dependency. The raw value must be preserved only as `region_as_reported`, not interpreted as geography.
