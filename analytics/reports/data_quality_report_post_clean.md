# Data Quality Report — Post-Clean

- **Generated at:** `2026-08-05T17:11:29.313781+00:00`
- **Code/commit reference:** `73a565f8882a8e80f7a57a26bea52fdcab1ff476`
- **Dataset row counts used:** customers=99,441, orders=99,441, order_items=112,650, products=32,951, sellers=3,095, order_payments=103,886, order_reviews=99,224, geolocation=1,000,163, product_category_translation=71

## Curated row counts

| Curated table | Rows |
|---|---:|
| `curated.customers` | 99,441 |
| `curated.orders` | 99,441 |
| `curated.order_items` | 112,650 |
| `curated.products` | 32,951 |
| `curated.sellers` | 3,095 |
| `curated.payment_details` | 103,886 |
| `curated.payment_summary` | 99,440 |
| `curated.reviews` | 99,224 |
| `curated.users` | 0 |
| `curated.refresh_tokens` | 0 |
| `curated.admin_settings` | 0 |
| `curated.data_refresh_log` | 4 |

## Cleaning diff

| Source → curated | Raw rows | Curated rows | Rows removed | Rationale |
|---|---:|---:|---:|---|
| `raw.customers` → `curated.customers` | 99,441 | 99,441 | 0 | required-key validation and grain deduplication |
| `raw.orders` → `curated.orders` | 99,441 | 99,441 | 0 | required fields, valid customer FK, timestamp ordering |
| `raw.order_items` → `curated.order_items` | 112,650 | 112,650 | 0 | required fields, non-negative values, valid FKs |
| `raw.products` → `curated.products` | 32,951 | 32,951 | 0 | required product_id and grain deduplication |
| `raw.sellers` → `curated.sellers` | 3,095 | 3,095 | 0 | required seller_id and grain deduplication |
| `raw.order_payments` → `curated.payment_details` | 103,886 | 103,886 | 0 | required fields, non-negative values, valid order FK |
| `raw.order_reviews` → `curated.reviews` | 99,224 | 99,224 | 0 | composite grain, score range, valid order FK |
| payment detail → `curated.payment_summary` | 103,886 | 99,440 | 4,446 | aggregated to one row per order |

### Invalid-data handling

Invalid rows are excluded only when they violate the binding curated contract. Optional nulls are retained.

| Invalid category | Rows detected | Rows dropped | Values corrected |
|---|---:|---:|---:|
| Customers missing required identifiers | 0 | 0 | 0 |
| Orders missing required fields | 0 | 0 | 0 |
| Orders with delivery before purchase | 0 | 0 | 0 |
| Order items with missing required fields or negative values | 0 | 0 | 0 |
| Payments with missing required fields or impossible values | 0 | 0 | 0 |
| Reviews with missing required fields or invalid score | 0 | 0 | 0 |

### Duplicate handling

| Raw table | Grain | Duplicate extra rows removed |
|---|---|---:|
| `raw.customers` | customer_id | 0 |
| `raw.orders` | order_id | 0 |
| `raw.order_items` | order_id, order_item_id | 0 |
| `raw.products` | product_id | 0 |
| `raw.sellers` | seller_id | 0 |
| `raw.order_payments` | order_id, payment_sequential | 0 |
| `raw.order_reviews` | review_id, order_id | 0 |
| `raw.geolocation` | source has no unique grain | 0 |
| `raw.product_category_translation` | product_category_name | 0 |

### Values imputed or enriched

| Category | Count | Rationale |
|---|---:|---|
| Source values imputed | 0 | Optional source nulls are retained; no value is fabricated. |
| Customer ZIP prefixes without geolocation match | 278 | Coordinates remain NULL. |
| Seller ZIP prefixes without geolocation match | 7 | Coordinates remain NULL. |
| Matched coordinates | See curated non-null coordinates | Independent median latitude/longitude per ZIP prefix. |

### Review duplicate consistency

- Duplicate `review_id` groups preserved across orders: **789**
- Groups with inconsistent score/title/message: **0**
- Review-grain downstream analysis must use one deterministic row per `review_id`.

## Retained outlier flags

All flagged rows remain in curated tables.

| Field | Q1 | Q3 | IQR | Lower | Upper | Flagged | Flagged % | Persisted flag count |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `price` | 39.9000 | 134.9000 | 95.0000 | -102.6000 | 277.4000 | 8,427 | 7.4807% | 8,427 |
| `freight_value` | 13.0800 | 21.1500 | 8.0700 | 0.9750 | 33.2550 | 12,134 | 10.7714% | 12,134 |
| `payment_value` | 56.7900 | 171.8375 | 115.0475 | -115.7813 | 344.4088 | 7,981 | 7.6825% | 7,981 |
| `delivery_days` | 6.0000 | 15.0000 | 9.0000 | -7.5000 | 28.5000 | 5,025 | 5.2085% | 5,025 |
