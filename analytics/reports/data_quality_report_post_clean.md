# Data Quality Report — Post-Clean

- **Generated at:** `2026-08-17T11:53:32.476036+00:00`
- **Code/commit reference:** `18eb91c50260b131d20baa6fe04d36db493fe2ee`
- **Dataset row counts used:** store_transactions=100,000

## Curated row counts

| Curated table | Rows |
|---|---:|
| `curated.customers` | 100,000 |
| `curated.products` | 100,000 |
| `curated.orders` | 100,000 |
| `curated.state_geocode` | 10 |
| `curated.state_region_reference` | 10 |
| `curated.users` | 0 |
| `curated.refresh_tokens` | 0 |
| `curated.admin_settings` | 0 |
| `curated.data_refresh_log` | 18 |

## Cleaning diff

| Source → curated | Raw rows | Curated rows | Rows removed | Rationale |
|---|---:|---:|---:|---|
| source → `customers` | 100,000 | 100,000 | 0 | required fields + Customer ID deduplication |
| source → `products` | 100,000 | 100,000 | 0 | required fields + Product ID deduplication |
| source → `orders` | 100,000 | 100,000 | 0 | valid dates/financials/FKs + Order ID deduplication |

### Invalid-data handling

| Category | Rows detected | Rows dropped | Values corrected |
|---|---:|---:|---:|
| Invalid customer fields | 0 | 0 | 0 |
| Invalid product fields | 0 | 0 | 0 |
| Invalid order fields or impossible values | 0 | 0 | 0 |
| Discount scale normalization | 100,000 | 0 | 100,000 |

Discount values were converted from source fractions (`0.00–0.50`) to percentage points (`0–50`) to satisfy the curated `discount_pct` contract.
No source value was imputed or fabricated.

### Date-field anomaly

`Year` disagrees with the year of `Order Date` on **80,023 rows (80.0230%)**. `Year` and `Sales Date` remain raw-only audit fields; curated orders use the v2.0 binding `order_date` and no source date is silently overwritten.

### Duplicate handling

| Grain | Duplicate extra rows removed |
|---|---:|
| Order ID | 0 |
| Customer ID | 0 |
| Product ID | 0 |

## Retained outlier flags

Legitimate outliers remain in `curated.orders`; flags are analytical indicators.

| Flag | Persisted rows |
|---|---:|
| `is_sales_outlier` | 0 |
| `is_profit_outlier` | 1,213 |

## Geographic integrity anomaly — binding v2.1 finding

The source contains **10 states × 4 reported regions = 40 distinct state/region pairs**. Every state occurs in North, South, East, and West, so `region` is not geographically reliable and is preserved only as `curated.customers.region_as_reported`. It must never be labeled as real geography. Geographic consumers must join `state_region_reference` instead.

## Static reference provenance

- State centroids: [DataMeet India state boundaries](https://github.com/datameet/maps/tree/b3fbbde595310b397a55d718e0958ce249a4fa1f/States), CC BY 4.0; polygon centroids calculated from the pinned shapefile commit.
- State regions: [Government of India Ministry of Housing and Urban Affairs regional classification](https://mohua.gov.in/upload/uploadfiles/files/4Empanelment_of_Resource.pdf); the 10 represented states map to North, East, West, or South under its R1–R4 groups.
