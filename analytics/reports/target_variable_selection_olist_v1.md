# Target Variable Selection Report

- **Generated at:** `2026-08-08T03:42:27.6703354Z`
- **Code/commit reference:** `3f85f4ac7ca165b7aa81ce9fde1dd57269d886d3`
- **Dataset row counts used:** orders=99,441; delivered orders=96,478; delivered orders with both delivery dates=96,470; customers with a delivered order=93,358; review-order links=99,224; delivered review-order links=96,361; delivered orders with at least one review=95,832; order items=112,650
- **Observed purchase range for eligible orders:** `2016-09-15T12:16:38` to `2018-08-29T15:00:37`
- **Authority:** Addendum v1.3 → v1.2 → v1.1 → SRS v1.0
- **Metric contract:** delivered orders only for revenue/customer/CLV calculations; revenue is item price plus freight; purchase timestamp is the date axis.

## Decision

**Selected target: Customer Satisfaction Classification.** The model unit will be one delivered `(review_id, order_id)` link. The binary label is `low_satisfaction = 1` when `review_score <= 3`, and `low_satisfaction = 0` when `review_score >= 4`. The prediction point is after delivery facts are known but before the review is submitted, so delivery performance is predictive input while all review outcome fields remain excluded.

## Observed candidate evidence

| Candidate | Label availability and observed class balance | Feature evidence from Phase 3 / Phase 4 calculation |
|---|---|---|
| Repeat Customer | 93,358 delivered-order customers; 2,801 repeat customers; **3.0003% positive** | First-order revenue has negligible point-biserial association with ever-repeat status (`r=-0.0114`). The Phase 3 profile confirms an average of 1.0334 orders and requires temporal observation/outcome windows. |
| Customer Satisfaction | 96,361 delivered review-order links covering 95,832 / 96,478 delivered orders (**99.3304% order coverage**); 20,308 low (**21.0749%**) vs 76,053 high (**78.9251%**) | Review score correlates with delivery days (`r=-0.3341`) and delivery-delay days (`r=-0.2673`). Late reviews average 2.5665 vs 4.2937 on time; Welch `t=89.5507`, `p<0.0001`. Low-satisfaction association is also visible for item count (`r=0.1111`), freight (`r=0.0801`), category (Cramér's V `0.0808`), and customer state (Cramér's V `0.0779`). |
| Late Delivery | 96,470 / 96,478 delivered orders have both dates (**99.9917% coverage**); 7,826 late (**8.1124%**) vs 88,644 on time | Customer state has Cramér's V `0.1287` with lateness, consistent with the Phase 3 state ANOVA (`F=781.8406`, `p<0.0001`). Pre-outcome numeric associations are weak: freight `r=0.0253`, average item price `r=0.0213`, revenue `r=0.0175`, item count `r=-0.0158`. |
| High-Value Customer | 93,358 delivered-order customers; top-20% threshold is historical CLV **BRL 208.532**; 18,672 positives (**20.0004%**) | First-order revenue has strong association with the full-history label (`r=0.5946`), but full-history spend is part of the target definition. A valid future-value model must isolate observation and outcome windows so this signal does not become leakage. |

The source's **58.7025% null rate applies to `review_comment_message`**, not `review_score`; it is relevant to the Phase 6 NLP gate but does not reduce satisfaction-label coverage. The prompt's approximate 6.77% late rate was rechecked against the binding definition: the actual delivered-order rate is **8.1124%** (7,826 / 96,470).

## Scoring method

All five SRS §5.3 criteria use an unweighted 1–5 ordinal score. Availability is rated from observed label coverage; balance is rated from the observed minority share; business value follows the SRS retail levers; feature support uses measured effect/association evidence rather than p-values alone; feasibility accounts for label clarity, imbalance, leakage control, and required temporal design. No criterion is weighted, so the total is the simple row sum.

| Candidate | Data availability | Class balance | Business value | Feature support | Feasibility | Total |
|---|---:|---:|---:|---:|---:|---:|
| Repeat Customer Prediction | 5 | 1 | 5 | 1 | 2 | **14** |
| Customer Satisfaction Classification | 5 | 4 | 5 | 5 | 5 | **24** |
| Late Delivery Classification | 5 | 2 | 5 | 3 | 4 | **19** |
| High-Value Customer Classification | 5 | 4 | 5 | 4 | 3 | **21** |

### Score rationale

- **Repeat Customer:** complete customer-profile availability and high retention value do not offset the 3.0003% positive class, negligible first-order association, and mandatory cohort/time-window design.
- **Customer Satisfaction:** near-complete order coverage, a usable 21.07/78.93 split, strong operational value, multiple statistically supported delivery/product signals, and a clear pre-review prediction point produce the highest score.
- **Late Delivery:** the label is almost completely available and operationally clear, but the 8.1124% minority class and weak measured pre-outcome numeric associations lower balance and feature-support scores.
- **High-Value Customer:** the designed top-20% class is usable and first-order spend is strongly associated, but the apparent signal partially overlaps the full-history label definition; temporal windows and leakage controls make it less immediately feasible than satisfaction.

The winner leads the next candidate by three points, so the SRS within-one-point tie-break is not invoked.

## Validation Strategy

Use a reproducible stratified, group-aware 80/20 train/test split with `RANDOM_SEED=42`, stratifying on `low_satisfaction` and grouping by `order_id`. Grouping is required because 525 delivered orders have multiple review links (529 extra links), and 189 of those order groups contain more than one score; no order may appear in both train and test through duplicated order features. Model selection inside the training partition will use group-aware stratified cross-validation. The untouched test partition is evaluated once. Primary selection metric remains F1 per SRS §13.1, with ROC-AUC as the tie-breaker; class-weighting is evaluated inside training only.

This is an outcome-at-resolution target, so Addendum v1.1 §11 permits a stratified random split. No behavioral observation/outcome window is required. The grouping refinement prevents order-level duplication leakage without changing that authorized strategy.

## Leakage exclusions

The following fields are excluded from all model inputs because they reveal or directly encode the review outcome:

- `review_score` and the derived `low_satisfaction` label.
- `review_id` and `order_id` as predictive features (retained only for grouping/audit).
- `comment_title`, `comment_message`, `review_creation_ts`, and `review_answer_ts`.
- Any review-derived aggregate, sentiment, topic, keyword, or text-presence indicator.
- Any post-review recommendation, prediction, or model-output field.

Delivery outcome fields (`delivered_customer_ts`, `delivery_days`, `delivery_delay_days`, `is_late`) are permitted because the declared prediction point is after delivery and before review submission. Purchase, payment, product, seller, category, freight, geography, and shipping-limit features are permitted only when timestamp checks confirm they are available by that prediction point. Dataset-wide RFM segment, historical CLV, future orders, and any aggregate calculated beyond the order's review time are excluded unless rebuilt strictly as-of that timestamp.

## Business justification

Customer satisfaction is the most defensible first classification problem because nearly every delivered order has a usable score, the minority class is large enough for meaningful evaluation, and Phase 3 shows a clear operational relationship between delivery performance and review outcomes. The model can therefore help retail operations identify delivered orders at risk of a poor review before the customer submits feedback, enabling targeted service recovery. This supports business decision-making directly while keeping the project analytics-led: the classification target follows the observed delivery and review evidence rather than being assumed in advance.

## Phase gate

Phase 4 selects exactly one target and adds no training, preprocessing, feature-building, model registry, NLP, API, authentication, frontend, or Power BI implementation. Phase 6 must honor this target, validation strategy, prediction point, and leakage list unless a later authoritative addendum explicitly changes them.
