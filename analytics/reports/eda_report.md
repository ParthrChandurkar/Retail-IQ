# Exploratory Data Analysis Report

- **Generated at:** `2026-08-06T04:51:08.329076+00:00`
- **Code/commit reference:** `aa84a065ffa36b58a3f8f8b2b8523d7dad07a45c`
- **Dataset row counts used:** orders=99,441, payments=103,886, order_items=112,650, customers=99,441, customer_profile=93,358, reviews=99,224
- **Metric contract:** delivered orders only for revenue, orders, customers, AOV, and historical CLV; purchase timestamp is the date axis.


## Univariate analysis

| Field | N | Mean | Median | Mode | Variance | Std | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|---|
| price | 112650 | 120.6537 | 74.9900 | 59.9000 | 33,721.4195 | 183.6339 | 39.9000 | 134.9000 | 0.8500 | 6,735.0000 |
| freight_value | 112650 | 19.9903 | 16.2600 | 15.1000 | 249.8425 | 15.8064 | 13.0800 | 21.1500 | 0.0000 | 409.6800 |
| payment_value | 103886 | 154.1004 | 100.0000 | 50.0000 | 47,303.6678 | 217.4941 | 56.7900 | 171.8375 | 0.0000 | 13,664.0800 |
| delivery_days | 96476 | 12.0941 | 10.0000 | 7 | 91.2359 | 9.5517 | 6.0000 | 15.0000 | 0 | 209 |
| review_score | 98410 | 4.0888 | 5.0000 | 5 | 1.8111 | 1.3458 | 4.0000 | 5.0000 | 1 | 5 |

## Bivariate analysis

### Review score by delivery outcome

| Group | N | Mean | Median | Std |
|---|---|---|---|---|
| late | 7,700.0000 | 2.5665 | 2.0000 | 1.6583 |
| on_time | 88,653.0000 | 4.2937 | 5.0000 | 1.1478 |

### Average order value by primary payment type

| Payment type | Orders | AOV (BRL) |
|---|---|---|
| credit_card | 72825 | 166.1426 |
| boleto | 19191 | 144.3350 |
| voucher | 2977 | 114.8601 |
| debit_card | 1484 | 140.4468 |
| — | 1 | 143.4600 |

The executed EDA notebook contains the required price/freight scatter and delivery/review boxplot.

## Multivariate analysis

The executed notebook contains the full Pearson correlation heatmap across order revenue, item, freight, payment, installment, delivery, and order-grain review features.

## Monthly trend

| Month | Revenue (BRL) | Delivered orders |
|---|---|---|
| 2016-09-01 | 143.4600 | 1 |
| 2016-10-01 | 46,490.6600 | 265 |
| 2016-12-01 | 19.6200 | 1 |
| 2017-01-01 | 127,482.3700 | 750 |
| 2017-02-01 | 271,239.3200 | 1653 |
| 2017-03-01 | 414,330.9500 | 2546 |
| 2017-04-01 | 390,812.4000 | 2303 |
| 2017-05-01 | 566,851.4000 | 3546 |
| 2017-06-01 | 490,050.3700 | 3135 |
| 2017-07-01 | 566,299.0800 | 3872 |
| 2017-08-01 | 645,832.3600 | 4193 |
| 2017-09-01 | 701,077.4900 | 4150 |
| 2017-10-01 | 751,117.0100 | 4478 |
| 2017-11-01 | 1,153,364.2000 | 7289 |
| 2017-12-01 | 843,078.2900 | 5513 |
| 2018-01-01 | 1,077,887.4600 | 7069 |
| 2018-02-01 | 966,168.4100 | 6555 |
| 2018-03-01 | 1,120,598.2400 | 7003 |
| 2018-04-01 | 1,132,878.9300 | 6798 |
| 2018-05-01 | 1,128,774.5200 | 6749 |
| 2018-06-01 | 1,011,978.2900 | 6099 |
| 2018-07-01 | 1,027,807.2800 | 6159 |
| 2018-08-01 | 985,491.6400 | 6351 |

## Month-of-year seasonality

| Month | Average revenue | Average orders |
|---|---|---|
| 1 | 602,684.9150 | 3,909.5000 |
| 2 | 618,703.8650 | 4,104.0000 |
| 3 | 767,464.5950 | 4,774.5000 |
| 4 | 761,845.6650 | 4,550.5000 |
| 5 | 847,812.9600 | 5,147.5000 |
| 6 | 751,014.3300 | 4,617.0000 |
| 7 | 797,053.1800 | 5,015.5000 |
| 8 | 815,662.0000 | 5,272.0000 |
| 9 | 350,610.4750 | 2,075.5000 |
| 10 | 398,803.8350 | 2,371.5000 |
| 11 | 1,153,364.2000 | 7,289.0000 |
| 12 | 421,548.9550 | 2,757.0000 |

## Category-conditional Tukey follow-up

| Measure | Global flags | Category flags | Changed rows | Changed % of population |
|---|---|---|---|---|
| Price | 8427 | 9376 | 4071 | 3.6138 |
| Freight | 12134 | 9767 | 4179 | 3.7097 |

**Decision:** Category-conditional bounds replace global item flags because thousands of rows change classification and the global category mix is materially misleading. Source rows remain retained.

## Duplicate review consistency

Review-grain outputs use deterministic `DISTINCT ON (review_id)`. The source contains **789** duplicate-review groups; **0** disagree internally on score/title/message.
