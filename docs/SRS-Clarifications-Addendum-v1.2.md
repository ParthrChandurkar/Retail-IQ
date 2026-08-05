# Retail Business Intelligence Platform
## SRS Clarification Addendum v1.2

**Relationship to prior documents:** extends `SRS-Clarifications-Addendum.md` v1.1, which extends `SRS.md` v1.0. Resolves three data-reality questions raised during Phase 2, after all 9 raw CSVs were inspected. Updated authority order:

1. This document (v1.2)
2. SRS Clarification Addendum v1.1
3. Base SRS v1.0
4. No undocumented assumptions

---

### 18. `curated.reviews` — composite primary key (real duplicate `review_id`)

**Confirmed finding:** `review_id` is not globally unique in the source data — 789 groups link one `review_id` to multiple `order_id`s. This reflects Olist's real behavior of applying a single review answer across a multi-order purchase event; it is not a data error to silently deduplicate away.

**Approved resolution** — replaces the `review_id VARCHAR PRIMARY KEY` line in `SRS.md` §8.2:
```sql
CREATE TABLE curated.reviews (
    review_id             VARCHAR NOT NULL,
    order_id                VARCHAR NOT NULL REFERENCES curated.orders(order_id),
    review_score               SMALLINT NOT NULL CHECK (review_score BETWEEN 1 AND 5),
    comment_title                 TEXT,
    comment_message                 TEXT,
    review_creation_ts                 TIMESTAMP,
    review_answer_ts                     TIMESTAMP,
    PRIMARY KEY (review_id, order_id)
);
CREATE INDEX ix_reviews_review_id ON curated.reviews (review_id);
```

**Binding grain rule for every downstream consumer:**
- **Order-grain analysis** (does this order have a review, review score vs. delivery lateness, Late-Delivery/Satisfaction candidate-target feature building — SRS §5.3, §12.2) reads `curated.reviews` as-is, one row per `(review_id, order_id)`. This is correct: the review outcome genuinely applies to each linked order.
- **Review-grain analysis** (review-score distribution as a standalone metric, NLP/sentiment/topic modeling on comment text, word clouds — SRS §12.2 baseline stats and §14) **must** deduplicate to one row per `review_id` first, using `SELECT DISTINCT ON (review_id) ... ORDER BY review_id, order_id` (deterministic tie-break), or scores/text get double- or triple-counted.
- Before relying on that dedup, the post-clean data quality report must confirm score/text actually match across each duplicate group (expected, since it's the same review answer). Any group that disagrees internally is a genuine anomaly and must be flagged explicitly in the report, not silently resolved by picking one side.

### 19. Outlier flagging — Tukey's 1.5×IQR, approved with one follow-up condition

**Approved**, with the four columns exactly as proposed:

| Column | Type | Null handling |
|---|---|---|
| `orders.is_delivery_days_outlier` | `BOOLEAN` | **Nullable.** Bounds computed only over delivered orders (non-null `delivery_days`); rows without a `delivery_days` value get `NULL` — outlier status is undefined for them, not `FALSE`. |
| `order_items.is_price_outlier` | `BOOLEAN NOT NULL DEFAULT FALSE` | — |
| `order_items.is_freight_value_outlier` | `BOOLEAN NOT NULL DEFAULT FALSE` | — |
| `payment_details.is_payment_value_outlier` | `BOOLEAN NOT NULL DEFAULT FALSE` | — |

**Method:** standard Tukey rule, bounds = `[Q1 − 1.5×IQR, Q3 + 1.5×IQR]`, computed **globally** (one set of bounds per column, not per-category) for Phase 2.

**Non-blocking follow-up, binding for Phase 3/6:** global bounds will over-flag legitimately expensive items in high-price categories purely because of category mix, which risks working against the exact thing Addendum §16 protects — a high-value order is precisely what the High-Value-Customer candidate target needs to keep visible. Phase 3's EDA must explicitly check whether category-conditional IQR bounds materially change the flagged population and document the finding; recompute per-category only if that evidence shows the global flag is misleading, otherwise the global version stands. Phase 6 (ML feature engineering) must not use these flags as an automatic row-exclusion filter without checking the Phase 3 finding first.

The post-clean data quality report (Addendum §1) must state, per flagged column: computed Q1/Q3/IQR, lower/upper bounds, and count + percentage flagged.

### 20. Geolocation — median lat/lng per ZIP prefix, confirmed

Confirmed as binding (this was the SRS §4 "e.g. median" suggestion — now made explicit rather than left as an example): for each `zip_code_prefix`, `latitude = MEDIAN(latitude)` and `longitude = MEDIAN(longitude)`, computed **independently per coordinate** (not a true 2D geometric median) across all `raw.geolocation` rows sharing that prefix. Applies identically when populating both `curated.customers.latitude/longitude` and `curated.sellers.latitude/longitude` via the zip-prefix join.

**Edge cases:** a prefix with exactly one observation uses that value trivially. A prefix with zero matching geolocation rows leaves `latitude`/`longitude` as `NULL` — never fabricated, never defaulted to a state/country centroid. Report the unmatched-prefix count in the post-clean data quality report.

---

*Phase 2 is authorized to resume on receipt of this addendum.*