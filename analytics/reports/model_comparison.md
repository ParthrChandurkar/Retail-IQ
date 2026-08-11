# Model Comparison — Customer Satisfaction

- **Generated at:** `2026-08-11T18:07:06.865651Z`
- **Dataset row counts used:** review-order links=96,361; train=77,069; test=19,292; unique orders=95,832
- **Code/commit reference:** `23f76a939e5e2e603a17370762a4a09e0c2e05a1`
- **Positive class:** `low_satisfaction` (`review_score <= 3`)
- **Validation:** group-aware stratified 80/20 split and 5-fold training CV; seed 42

Precision, Recall, F1, and CV F1 below are for `low_satisfaction` only; they are not macro- or weighted-averaged.

| Algorithm | Accuracy | Precision | Recall | F1 | ROC-AUC | CV Mean F1 (5-fold) |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7456 | 0.4197 | 0.5004 | 0.4565 | 0.7043 | 0.4496 |
| Decision Tree | 0.8080 | 0.6100 | 0.2787 | 0.3826 | 0.6623 | 0.3652 |
| Random Forest | 0.8251 | 0.8000 | 0.2408 | 0.3702 | 0.7130 | 0.3662 |
| Gradient Boosting | 0.8252 | 0.7856 | 0.2491 | 0.3782 | 0.7105 | 0.3760 |
| XGBoost | 0.8246 | 0.7801 | 0.2488 | 0.3773 | 0.7145 | 0.3746 |

## Selected model

**Logistic Regression** (`model_id=3`) is selected by highest training-only mean CV positive-class F1, with mean CV ROC-AUC as the declared tiebreaker. The held-out test metrics are final evaluation evidence, not selection input.

## Labeled confusion matrix

Rows are actual labels; columns are predicted labels.

| Actual \ Predicted | low_satisfaction | high_satisfaction |
|---|---:|---:|
| low_satisfaction | 2061 | 2058 |
| high_satisfaction | 2850 | 12323 |

## Top-10 global feature importances

| Rank | Feature | Importance | Business interpretation |
|---:|---|---:|---|
| 1 | `is_late` | 0.184664 | Whether an order missed its promise materially changes satisfaction risk. |
| 2 | `delivery_days` | 0.160138 | Delivery experience is a major observable driver of review risk. |
| 3 | `payment_value` | 0.138322 | This operational input contributes materially to the model's global decisions. |
| 4 | `item_count` | 0.133566 | — |
| 5 | `seller_count` | 0.093342 | — |
| 6 | `total_price` | 0.069526 | — |
| 7 | `average_item_price` | 0.064384 | — |
| 8 | `estimated_delivery_days` | 0.041671 | — |
| 9 | `maximum_item_price` | 0.020573 | — |
| 10 | `approval_hours` | 0.016233 | — |

## Selection note

Every algorithm used the identical feature frame, fitted preprocessing definition, held-out order-group split, and five group-aware CV folds. Class weighting was evaluated inside training: balanced Logistic Regression improved mean training-CV positive-class F1 from 0.3874 to 0.4496, so the balanced variant was retained. The untouched 20% test partition was used once for the comparison above. SHAP was not implemented; the API intentionally omits `local_shap_contributions`.
