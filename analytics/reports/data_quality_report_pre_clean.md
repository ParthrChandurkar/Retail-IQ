# Data Quality Report — Pre-Clean

- **Generated at:** `2026-08-05T17:10:21.478435+00:00`
- **Code/commit reference:** `73a565f8882a8e80f7a57a26bea52fdcab1ff476`
- **Dataset row counts used:** customers=99,441, orders=99,441, order_items=112,650, products=32,951, sellers=3,095, order_payments=103,886, order_reviews=99,224, geolocation=1,000,163, product_category_translation=71

## Source row counts

| Raw table | Actual rows | SRS approximate rows | Difference |
|---|---:|---:|---:|
| `raw.customers` | 99,441 | 99,000 | +441 |
| `raw.orders` | 99,441 | 99,000 | +441 |
| `raw.order_items` | 112,650 | 112,000 | +650 |
| `raw.products` | 32,951 | 33,000 | -49 |
| `raw.sellers` | 3,095 | 3,000 | +95 |
| `raw.order_payments` | 103,886 | 104,000 | -114 |
| `raw.order_reviews` | 99,224 | 99,000 | +224 |
| `raw.geolocation` | 1,000,163 | 1,000,000 | +163 |
| `raw.product_category_translation` | 71 | 71 | +0 |

## Column null rates

| Column | Null count | Null percentage |
|---|---:|---:|
| `raw.customers.customer_id` | 0 | 0.0000% |
| `raw.customers.customer_unique_id` | 0 | 0.0000% |
| `raw.customers.customer_zip_code_prefix` | 0 | 0.0000% |
| `raw.customers.customer_city` | 0 | 0.0000% |
| `raw.customers.customer_state` | 0 | 0.0000% |
| `raw.orders.order_id` | 0 | 0.0000% |
| `raw.orders.customer_id` | 0 | 0.0000% |
| `raw.orders.order_status` | 0 | 0.0000% |
| `raw.orders.order_purchase_timestamp` | 0 | 0.0000% |
| `raw.orders.order_approved_at` | 160 | 0.1609% |
| `raw.orders.order_delivered_carrier_date` | 1,783 | 1.7930% |
| `raw.orders.order_delivered_customer_date` | 2,965 | 2.9817% |
| `raw.orders.order_estimated_delivery_date` | 0 | 0.0000% |
| `raw.order_items.order_id` | 0 | 0.0000% |
| `raw.order_items.order_item_id` | 0 | 0.0000% |
| `raw.order_items.product_id` | 0 | 0.0000% |
| `raw.order_items.seller_id` | 0 | 0.0000% |
| `raw.order_items.shipping_limit_date` | 0 | 0.0000% |
| `raw.order_items.price` | 0 | 0.0000% |
| `raw.order_items.freight_value` | 0 | 0.0000% |
| `raw.products.product_id` | 0 | 0.0000% |
| `raw.products.product_category_name` | 610 | 1.8512% |
| `raw.products.product_name_lenght` | 610 | 1.8512% |
| `raw.products.product_description_lenght` | 610 | 1.8512% |
| `raw.products.product_photos_qty` | 610 | 1.8512% |
| `raw.products.product_weight_g` | 2 | 0.0061% |
| `raw.products.product_length_cm` | 2 | 0.0061% |
| `raw.products.product_height_cm` | 2 | 0.0061% |
| `raw.products.product_width_cm` | 2 | 0.0061% |
| `raw.sellers.seller_id` | 0 | 0.0000% |
| `raw.sellers.seller_zip_code_prefix` | 0 | 0.0000% |
| `raw.sellers.seller_city` | 0 | 0.0000% |
| `raw.sellers.seller_state` | 0 | 0.0000% |
| `raw.order_payments.order_id` | 0 | 0.0000% |
| `raw.order_payments.payment_sequential` | 0 | 0.0000% |
| `raw.order_payments.payment_type` | 0 | 0.0000% |
| `raw.order_payments.payment_installments` | 0 | 0.0000% |
| `raw.order_payments.payment_value` | 0 | 0.0000% |
| `raw.order_reviews.review_id` | 0 | 0.0000% |
| `raw.order_reviews.order_id` | 0 | 0.0000% |
| `raw.order_reviews.review_score` | 0 | 0.0000% |
| `raw.order_reviews.review_comment_title` | 87,656 | 88.3415% |
| `raw.order_reviews.review_comment_message` | 58,247 | 58.7025% |
| `raw.order_reviews.review_creation_date` | 0 | 0.0000% |
| `raw.order_reviews.review_answer_timestamp` | 0 | 0.0000% |
| `raw.geolocation.geolocation_zip_code_prefix` | 0 | 0.0000% |
| `raw.geolocation.geolocation_lat` | 0 | 0.0000% |
| `raw.geolocation.geolocation_lng` | 0 | 0.0000% |
| `raw.geolocation.geolocation_city` | 0 | 0.0000% |
| `raw.geolocation.geolocation_state` | 0 | 0.0000% |
| `raw.product_category_translation.product_category_name` | 0 | 0.0000% |
| `raw.product_category_translation.product_category_name_english` | 0 | 0.0000% |

## Duplicate rates at declared grain

| Raw table | Declared grain | Duplicate extra rows |
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

## Referential-integrity risks

| Relationship | Orphan rows |
|---|---:|
| orders.customer_id → customers.customer_id | 0 |
| order_items.order_id → orders.order_id | 0 |
| order_items.product_id → products.product_id | 0 |
| order_items.seller_id → sellers.seller_id | 0 |
| order_payments.order_id → orders.order_id | 0 |
| order_reviews.order_id → orders.order_id | 0 |

## Global Tukey outlier candidates

These are diagnostic flags only. No source row is deleted.

| Field | Q1 | Q3 | IQR | Lower | Upper | Flagged | Flagged % |
|---|---:|---:|---:|---:|---:|---:|---:|
| `price` | 39.9000 | 134.9000 | 95.0000 | -102.6000 | 277.4000 | 8,427 | 7.4807% |
| `freight_value` | 13.0800 | 21.1500 | 8.0700 | 0.9750 | 33.2550 | 12,134 | 10.7714% |
| `payment_value` | 56.7900 | 171.8375 | 115.0475 | -115.7813 | 344.4088 | 7,981 | 7.6825% |
| `delivery_days` | 6.0000 | 15.0000 | 9.0000 | -7.5000 | 28.5000 | 5,025 | 5.2085% |
