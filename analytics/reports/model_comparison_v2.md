# Migration M6 Model Comparison — High-Profit Order

- **Generated at:** `2026-08-20T08:36:31.110802Z`
- **Dataset row counts used:** orders=100,000; train=80,000; test=20,000
- **Code/commit reference:** `cc30e425477a`
- **Features:** `sales, discount_pct, order_month, order_dow, category, sub_category, segment, city_type, state, region`
- **Positive class:** `high_profit_order` (`profit >= INR 5,363.845`)
- **Negative class:** `standard_profit_order`
- **Validation:** order-grain stratified 80/20 split and five-fold stratified training CV; seed 42

Precision, Recall, F1, and CV F1 are for `high_profit_order` only; they are not macro- or weighted-averaged.

| Algorithm | Accuracy | Precision | Recall | F1 | ROC-AUC | CV Mean F1 | CV Mean ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.847300 | 0.710697 | 0.656400 | 0.682470 | 0.922866 | 0.683974 | 0.923523 |
| Decision Tree | 0.832650 | 0.668570 | 0.655600 | 0.662022 | 0.896684 | 0.663529 | 0.895844 |
| Random Forest | 0.846550 | 0.706967 | 0.659600 | 0.682462 | 0.921096 | 0.685159 | 0.921642 |
| Gradient Boosting | 0.848750 | 0.682769 | 0.737800 | 0.709218 | 0.923453 | 0.712965 | 0.924240 |
| XGBoost | 0.848300 | 0.688531 | 0.718000 | 0.702957 | 0.923165 | 0.705856 | 0.923642 |

## Selected model

**Gradient Boosting** (`model_id=4`) was selected by highest training-CV positive-class F1; mean CV ROC-AUC was the declared tiebreaker. The held-out test partition was not used for selection.

The highest held-out accuracy belongs to **Gradient Boosting**. Accuracy and positive-class F1 select the same algorithm in this migration.

## Labeled confusion matrix

Rows are actual labels; columns are predicted labels.

| Actual \ Predicted | high_profit_order | standard_profit_order |
|---|---:|---:|
| high_profit_order | 3689 | 1311 |
| standard_profit_order | 1714 | 13286 |

## Top-10 global feature importances

| Rank | Feature | Importance | Business interpretation |
|---:|---|---:|---|
| 1 | `sales` | 0.808818 | Checkout sales value is the strongest commercial signal of high-profit orders. |
| 2 | `discount_pct` | 0.190572 | Applied discount changes the margin available from an order before fulfilment. |
| 3 | `order_month` | 0.000098 | Order timing captures any repeatable checkout seasonality. |
| 4 | `order_dow` | 0.000070 | — |
| 5 | `sub_category_Fries` | 0.000062 | — |
| 6 | `sub_category_Carrots` | 0.000059 | — |
| 7 | `sub_category_Mangoes` | 0.000053 | — |
| 8 | `sub_category_Chairs` | 0.000050 | — |
| 9 | `state_Karnataka` | 0.000033 | — |
| 10 | `state_Madhya Pradesh` | 0.000031 | — |

SHAP was not implemented. No local SHAP contribution field or fabricated explanation is emitted.

## Prediction contract examples

These examples were generated from real held-out rows through the selected registered pipeline. They are model-contract examples for M7; no API router was changed in M6.

### Example 1: `high_profit_order`

Request:

```json
{
  "category": "Sessional Fruits & Vegetables",
  "city_type": "Tier 2",
  "discount_pct": 14.0,
  "order_dow": 7,
  "order_month": 7,
  "region": "South",
  "sales": 46837.74,
  "segment": "Corporate",
  "state": "Tamil Nadu",
  "sub_category": "Carrots"
}
```

Response:

```json
{
  "predicted_label": "high_profit_order",
  "predicted_probability": 0.8327976187991819
}
```

### Example 2: `standard_profit_order`

Request:

```json
{
  "category": "Household Items",
  "city_type": "Village",
  "discount_pct": 33.0,
  "order_dow": 5,
  "order_month": 10,
  "region": "North",
  "sales": 18928.78,
  "segment": "Corporate",
  "state": "Uttar Pradesh",
  "sub_category": "Utensils"
}
```

Response:

```json
{
  "predicted_label": "standard_profit_order",
  "predicted_probability": 0.9975690000606111
}
```

`predicted_probability` is confidence in the returned label: P(high-profit) for `high_profit_order`, and `1 - P(high-profit)` for `standard_profit_order`.

## Retirement and phase boundary

Registration removed **3** Olist-era `low_satisfaction` registry rows, their prediction/importance rows, and their joblib artifacts. Exactly one migrated active model remains. No NLP work was performed (N/A), and no API router or frontend file was changed.
