# Retail Business Intelligence Platform
## SRS Clarification Addendum v1.4

**Relationship to prior documents:** extends v1.3 → v1.2 → v1.1 → `SRS.md` v1.0. Closes one gap that was flagged in the original Phase-0 review's "Suggested improvements" list but never actually bound in v1.1–v1.3: positive-class definition and metric-averaging convention for the classification target. This must be resolved before Phase 6 training begins — it directly determines what `predicted_probability` means in the API contract. Updated authority order:

1. This document (v1.4)
2. SRS Clarification Addendum v1.3
3. SRS Clarification Addendum v1.2
4. SRS Clarification Addendum v1.1
5. Base SRS v1.0
6. No undocumented assumptions

---

### 22. Positive class, metric averaging, and probability semantics (binding)

**Target (from `analytics/reports/target_variable_selection.md`, Phase 4):** Customer Satisfaction — `review_score ≤ 3` (low) vs. `review_score ≥ 4` (high).

**Positive class = `low_satisfaction`.** Not the majority/default class — the class the business actually wants the model to catch. This mirrors standard convention for "detect the bad outcome" classifiers (churn, fraud, late delivery) and matches the recommendation engine's satisfaction-improvement flag (Addendum §12.4 / SRS §12.4), which exists to surface at-risk orders/segments, not to confirm satisfied ones.

**Metric reporting (binding for `model_comparison.md`, `/classification/metrics`, and any dashboard display):**
- Precision, Recall, and F1 are reported **for the positive class (`low_satisfaction`) specifically** — not macro-averaged, not weighted-averaged. A macro/weighted average would dilute the metric that matters (correctly catching dissatisfied customers) with trivial majority-class performance, given the ~21%/79% split reported in Phase 4.
- Accuracy and ROC-AUC are reported as usual (threshold-independent for ROC-AUC; no positive-class ambiguity for either).
- The confusion matrix returned by `/classification/metrics` must be explicitly labeled (row/column headers `low_satisfaction` / `high_satisfaction`), never a bare unlabeled 2×2 array.

**`predicted_probability` semantics (binding for `POST /classification/predict`):** the probability is of **whatever `predicted_label` the model actually output** — i.e. confidence in the prediction, not always P(positive). If `predicted_label = "low_satisfaction"`, `predicted_probability` is P(low_satisfaction). If `predicted_label = "high_satisfaction"`, `predicted_probability` is P(high_satisfaction) = 1 − P(low_satisfaction). This matches the convention already implied by the original SRS §13.3 example (`"predicted_label": "on_time", "predicted_probability": 0.87` — confidence in the predicted outcome, not a fixed reference class) and is the more intuitive reading for a non-technical dashboard user ("87% confident this customer will be satisfied" reads correctly either way).

**`predicted_label` values** are the literal strings `"low_satisfaction"` / `"high_satisfaction"` — not `0`/`1`, not `"low"`/`"high"` — for self-documenting API responses.
