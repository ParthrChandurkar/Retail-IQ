# Customer Analytics Report

> **Superseded Olist-era record.** Retained for migration history only; RFM and
> CLV are not part of the active Indian Store Data product.

- **Generated at:** `2026-08-06T04:51:08.329076+00:00`
- **Code/commit reference:** `aa84a065ffa36b58a3f8f8b2b8523d7dad07a45c`
- **Dataset row counts used:** orders=99,441, payments=103,886, order_items=112,650, customers=99,441, customer_profile=93,358, reviews=99,224
- **Metric contract:** delivered orders only for revenue, orders, customers, AOV, and historical CLV; purchase timestamp is the date axis.


## Customer overview

| Customers | Repeat customers | Repeat rate % | Average orders | Average CLV | Median CLV |
|---|---|---|---|---|---|
| 93358 | 2801 | 3.0003 | 1.0334 | 165.1682 | 107.7800 |

## RFM segments

| Segment | Customers | Average historical CLV | Average orders |
|---|---|---|---|
| Hibernating | 36347 | 161.8133 | 1.0000 |
| New | 36140 | 164.3102 | 1.0000 |
| Promising | 18070 | 151.4104 | 1.0000 |
| At Risk | 996 | 293.8703 | 2.0813 |
| Champions | 985 | 372.4613 | 2.1817 |
| Loyal | 820 | 249.5345 | 2.0720 |

## Time between delivered orders

| Observed gaps | Average days | Median days |
|---|---|---|
| 3120 | 79.1503 | 29.4555 |

## Top customer states

| State | Customers | Average orders | Average CLV |
|---|---|---|---|
| SP | 39139 | 1.0344 | 147.3750 |
| RJ | 11914 | 1.0367 | 172.5111 |
| MG | 10999 | 1.0327 | 165.4103 |
| RS | 5167 | 1.0344 | 166.7301 |
| PR | 4769 | 1.0331 | 164.0239 |
| SC | 3445 | 1.0290 | 172.6708 |
| BA | 3158 | 1.0317 | 187.2854 |
| DF | 2019 | 1.0322 | 171.6051 |
| ES | 1928 | 1.0353 | 164.8351 |
| GO | 1894 | 1.0343 | 176.6933 |

## Method

- RFM: Percent-rank quintiles, 1 (lowest) through 5 (highest); recency uses last purchase timestamp, so more recent is higher.
- CLV: Delivered-order item price plus freight, historical to date in BRL.
- Segmentation: Deterministic documented RFM rules; customer_segments is GROUP BY rfm_segment only.
