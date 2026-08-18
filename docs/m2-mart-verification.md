# Migration M2 Mart Verification

Generated: 2026-08-18 (Asia/Calcutta)

## Entity repetition confirmation

- Orders: 100,000 rows / 100,000 distinct Order IDs.
- Customers: 100,000 rows / 100,000 distinct Customer IDs; repetition rate 0.0000%.
- Products: 100,000 order rows / 100,000 distinct Product IDs; repeated Product-ID rows 0; repetition rate **0.0000%**; maximum Product-ID frequency 1.
- Product analytics therefore stops at the 6-category / 24 category–sub-category-pair level. Individual Product IDs are not ranked or interpreted as repeat-selling products.

## Final mart contract and populated counts

| Mart | Exact grain | Rows |
|---|---|---:|
| `revenue_daily` | `date` | 1,826 |
| `revenue_by_category` | `date, category, sub_category` | 39,298 |
| `revenue_by_region` | `date, state, region, city_type` | 45,963 |
| `shipping_performance` | `date, ship_mode, region` | 26,652 |
| `customer_profile` | `customer_id` | 100,000 |
| `customer_segments` | `segment, order_value_tier, city_type` | 24 |
| `category_discount_profit` | `category, sub_category, discount_band` | 96 |
| `kpi_snapshot` | singleton (`snapshot_id = 1`) | 1 |

Removed Olist marts: `seller_performance`, `payment_method_mix`, `review_summary`, and `delivery_performance`.

## Cross-sectional segmentation

The data-derived Order Value quartile boundaries are ₹12,618.03, ₹25,134.695, and ₹37,575.85. Each tier contains exactly 25,000 customers. The discount quartile boundaries are 13%, 25%, and 38%. No RFM Frequency, monetary-over-time, repeat-purchase metric, or CLV field exists in the M2 mart contract.

## Geographic integrity

All 100,000 `customer_profile.region` values match `curated.state_region_reference`. Only 24,769 source `region_as_reported` values happen to match the trusted mapping. The reported source value remains audit-only and is not used by any mart.

## Ship-mode integrity check

| Ship mode | Orders | Mean shipping days | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| Second Class | 24,944 | 3.973340 | 4 | 1 | 7 |
| Same Day | 25,007 | 3.988523 | 4 | 1 | 7 |
| First Class | 25,078 | 3.999482 | 4 | 1 | 7 |
| Standard Class | 24,971 | 4.002843 | 4 | 1 | 7 |

One-way ANOVA gives F = 1.096041, p = 0.349304, and η² = 0.0000329. A Kruskal–Wallis check gives H = 3.295722 and p = 0.348238. Shipping duration is therefore effectively independent of the named ship mode and does not follow the expected service ordering. `shipping_performance` is retained only as a transparent descriptive mart. It must not be used as a service-quality claim or delayed-shipment label; M4 must not manufacture a ship-mode baseline from this field.

## Metric reconciliation and reproducibility

- Curated Revenue = mart Revenue = **₹2,508,441,014.18**.
- Curated Profit = mart Profit = **₹375,530,511.43**.
- AOV = **₹25,084.4101418**.
- Average Discount = **25.13199%**.
- Profit Margin = **14.9706733907%**.
- Two consecutive mart builds returned identical table counts.
- Migration `20260818_0007` passed downgrade → upgrade and a complete empty-database migration-chain rehearsal.
