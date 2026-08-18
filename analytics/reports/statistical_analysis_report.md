# Migration M3 Statistical Analysis

- **Generated at:** `2026-08-18T16:23:03.258209+00:00`
- **Code/commit reference:** `840a796`
- **Dataset row counts used:** customers=100,000, customer_profile=100,000, orders=100,000, raw_transactions=100,000, products=100,000
- **Metric contract:** all curated orders; Revenue=`SUM(sales)`, Profit=`SUM(profit)`, date axis=`order_date`, currency=INR.


All inferential decisions use α=0.05.

## Descriptive statistics

| Field | N | Mean | Median | Std | Q1 | Q3 |
|---|---|---|---|---|---|---|
| sales | 100000 | 25,084.4101 | 25,134.6950 | 14,403.1877 | 12,618.0300 | 37,575.8500 |
| profit | 100000 | 3,755.3051 | 3,317.4500 | 2,639.8520 | 1,651.1050 | 5,363.8450 |
| discount_pct | 100000 | 25.1320 | 25.0000 | 14.4324 | 13.0000 | 38.0000 |
| quantity | 100000 | 5.4938 | 5.0000 | 2.8761 | 3.0000 | 8.0000 |
| shipping_days | 100000 | 3.9911 | 4.0000 | 2.0066 | 2.0000 | 6.0000 |
| profit_margin_pct | 100000 | 14.9651 | 14.3926 | 5.2594 | 10.7946 | 18.5650 |

## Pearson correlation matrix

| Field | sales | profit | discount_pct | quantity | shipping_days | profit_margin_pct |
|---|---|---|---|---|---|---|
| sales | 1.0000 | 0.8180 | -8.0052e-05 | -0.0022 | 0.0005 | 0.0019 |
| profit | 0.8180 | 1.0000 | -0.2728 | -0.0038 | 0.0013 | 0.5001 |
| discount_pct | -8.0052e-05 | -0.2728 | 1.0000 | 0.0044 | -0.0026 | -0.5480 |
| quantity | -0.0022 | -0.0038 | 0.0044 | 1.0000 | 0.0050 | -0.0040 |
| shipping_days | 0.0005 | 0.0013 | -0.0026 | 0.0050 | 1.0000 | 0.0003 |
| profit_margin_pct | 0.0019 | 0.5001 | -0.5480 | -0.0040 | 0.0003 | 1.0000 |

## Covariance matrix

| Field | sales | profit | discount_pct | quantity | shipping_days | profit_margin_pct |
|---|---|---|---|---|---|---|
| sales | 207,451,815.5084 | 31,102,942.3122 | -16.6406 | -91.1824 | 15.4802 | 140.6170 |
| profit | 31,102,942.3122 | 6,968,818.7673 | -10,392.4407 | -28.6982 | 6.9928 | 6,943.0216 |
| discount_pct | -16.6406 | -10,392.4407 | 208.2950 | 0.1842 | -0.0754 | -41.5961 |
| quantity | -91.1824 | -28.6982 | 0.1842 | 8.2720 | 0.0287 | -0.0600 |
| shipping_days | 15.4802 | 6.9928 | -0.0754 | 0.0287 | 4.0263 | 0.0028 |
| profit_margin_pct | 140.6170 | 6,943.0216 | -41.5961 | -0.0600 | 0.0028 | 27.6618 |

## Required hypothesis tests

### Chi-Square: category × customer segment

- Null hypothesis: Product category and customer segment are independent.
- Statistic: `6.4108`
- p-value: `0.2683`
- Cramer's V: `0.0080`
- Degrees of freedom: `5`
- Conclusion: No statistically significant category preference difference was found between Consumer and Corporate buyers; the observed association is negligible.

### One-way ANOVA: profit margin across city types

- Null hypothesis: Mean profit margin is equal across city types.
- Statistic: `0.6369`
- p-value: `0.5289`
- Eta-squared: `1.2739e-05`
- Group means: `{'Tier 1': 14.985230815898564, 'Tier 2': 14.940045093948294, 'Village': 14.969717197981234}`
- Conclusion: Profit margins do not differ significantly across Tier 1, Tier 2, and Village orders; city type explains effectively none of the variation.

### Welch t-test: profit margin for high- vs low-discount orders

- Null hypothesis: Mean profit margin is equal for high- and low-discount orders.
- Statistic: `-188.4707`
- p-value: `<1e-300`
- Cohen's d: `-1.6334`
- Low group: ≤13.00% (n=26,706, mean margin=18.662281%)
- High group: ≥38.00% (n=25,281, mean margin=11.249826%)
- Conclusion: High-discount orders have a materially lower mean profit margin than low-discount orders; the difference is statistically significant and large.
