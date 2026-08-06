# Statistical Analysis Report

- **Generated at:** `2026-08-06T04:51:08.329076+00:00`
- **Code/commit reference:** `aa84a065ffa36b58a3f8f8b2b8523d7dad07a45c`
- **Dataset row counts used:** orders=99,441, payments=103,886, order_items=112,650, customers=99,441, customer_profile=93,358, reviews=99,224
- **Metric contract:** delivered orders only for revenue, orders, customers, AOV, and historical CLV; purchase timestamp is the date axis.


All inferential decisions use α = 0.05.

## Descriptive statistics

| Field | N | Mean | Median | Mode | Variance | Std | Q1 | Q3 |
|---|---|---|---|---|---|---|---|---|
| price | 112650 | 120.6537 | 74.9900 | 59.9000 | 33,721.4195 | 183.6339 | 39.9000 | 134.9000 |
| freight_value | 112650 | 19.9903 | 16.2600 | 15.1000 | 249.8425 | 15.8064 | 13.0800 | 21.1500 |
| payment_value | 103886 | 154.1004 | 100.0000 | 50.0000 | 47,303.6678 | 217.4941 | 56.7900 | 171.8375 |
| delivery_days | 96476 | 12.0941 | 10.0000 | 7 | 91.2359 | 9.5517 | 6.0000 | 15.0000 |
| review_score | 98410 | 4.0888 | 5.0000 | 5 | 1.8111 | 1.3458 | 4.0000 | 5.0000 |

## Pearson correlation matrix

| Field | order_revenue | avg_item_price | freight_value | item_count | total_payment_value | installments_max | delivery_days | delivery_delay_days | review_score |
|---|---|---|---|---|---|---|---|---|---|
| order_revenue | 1.0000 | 0.9209 | 0.4914 | 0.1899 | 1.0000 | 0.3199 | 0.0695 | -0.0177 | -0.0421 |
| avg_item_price | 0.9209 | 1.0000 | 0.2992 | -0.0587 | 0.9209 | 0.3165 | 0.0603 | -0.0068 | -0.0052 |
| freight_value | 0.4914 | 0.2992 | 1.0000 | 0.4394 | 0.4915 | 0.1992 | 0.1671 | -0.0493 | -0.0899 |
| item_count | 0.1899 | -0.0587 | 0.4394 | 1.0000 | 0.1900 | 0.0683 | -0.0191 | -0.0319 | -0.1234 |
| total_payment_value | 1.0000 | 0.9209 | 0.4915 | 0.1900 | 1.0000 | 0.3203 | 0.0695 | -0.0177 | -0.0421 |
| installments_max | 0.3199 | 0.3165 | 0.1992 | 0.0683 | 0.3203 | 1.0000 | 0.0519 | -0.0309 | -0.0310 |
| delivery_days | 0.0695 | 0.0603 | 0.1671 | -0.0191 | 0.0695 | 0.0519 | 1.0000 | 0.6078 | -0.3341 |
| delivery_delay_days | -0.0177 | -0.0068 | -0.0493 | -0.0319 | -0.0177 | -0.0309 | 0.6078 | 1.0000 | -0.2673 |
| review_score | -0.0421 | -0.0052 | -0.0899 | -0.1234 | -0.0421 | -0.0310 | -0.3341 | -0.2673 | 1.0000 |

## Covariance matrix

| Field | order_revenue | avg_item_price | freight_value | item_count | total_payment_value | installments_max | delivery_days | delivery_delay_days | review_score |
|---|---|---|---|---|---|---|---|---|---|
| order_revenue | 47,870.9101 | 38,223.5439 | 2,317.9072 | 22.3907 | 47,874.6495 | 189.8945 | 145.2235 | -39.4103 | -11.7484 |
| avg_item_price | 38,223.5439 | 35,985.3629 | 1,223.5896 | -6.0006 | 38,226.3421 | 162.8635 | 109.2633 | -13.0694 | -1.2451 |
| freight_value | 2,317.9072 | 1,223.5896 | 464.7990 | 5.1040 | 2,318.4956 | 11.6528 | 34.4125 | -10.8286 | -2.4850 |
| item_count | 22.3907 | -6.0006 | 5.1040 | 0.2903 | 22.3988 | 0.0998 | -0.0985 | -0.1749 | -0.0846 |
| total_payment_value | 47,874.6495 | 38,226.3421 | 2,318.4956 | 22.3988 | 47,879.1921 | 190.1038 | 145.3014 | -39.5010 | -11.7572 |
| installments_max | 189.8945 | 162.8635 | 11.6528 | 0.0998 | 190.1038 | 7.3589 | 1.3441 | -0.8537 | -0.1079 |
| delivery_days | 145.2235 | 109.2633 | 34.4125 | -0.0985 | 145.3014 | 1.3441 | 91.2289 | 59.1142 | -4.0596 |
| delivery_delay_days | -39.4103 | -13.0694 | -10.8286 | -0.1749 | -39.5010 | -0.8537 | 59.1142 | 103.6753 | -3.4689 |
| review_score | -11.7484 | -1.2451 | -2.4850 | -0.0846 | -11.7572 | -0.1079 | -4.0596 | -3.4689 | 1.6477 |

## Hypothesis tests

### Chi-Square: primary payment type × customer segment

- Null hypothesis: Primary payment type and customer segment are independent.
- Statistic: `393.8336`
- p-value: `1.3656e-74`
- Degrees of freedom: `15`
- Conclusion: The association between primary payment method and customer segment is statistically significant at α=0.05.

### One-way ANOVA: delivery days across customer states

- Null hypothesis: Mean delivery time is equal across customer states.
- Statistic: `781.8406`
- p-value: `0.0000`
- Conclusion: Differences in mean delivery time across states are statistically significant at α=0.05.

### Welch T-Test: review score for on-time vs late delivery

- Null hypothesis: Mean review score is equal for on-time and late deliveries.
- Statistic: `89.5507`
- p-value: `0.0000`
- Conclusion: Late deliveries have a lower mean review score than on-time deliveries; the difference is statistically significant at α=0.05.
