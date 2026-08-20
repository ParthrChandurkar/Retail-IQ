# Migration M5 Target Variable Selection

- **Generated at:** `2026-08-20T06:58:34.1530150Z`
- **Code/commit reference:** `3356f90b2b17`
- **Dataset rows used:** curated orders=100,000; customers=100,000; products=100,000
- **Authority:** Migration Addendum v2.2 → v2.1 → v2.0 → Clarification Addenda v1.4–v1.1 → SRS v1.0
- **Decision unit:** one completed order; the migrated dataset has exactly one row per order, customer, and product

## Decision

**Selected target: High-Profit Order Classification.** An order is a
`high_profit_order` when its realized `profit` is greater than or equal to the
fixed M4 75th-percentile threshold of **INR 5,363.845**. Otherwise it is a
`standard_profit_order`. The target has **25,000 positive rows (25.0000%)** and
**75,000 negative rows (75.0000%)**.

The prediction point is checkout, after the order's product mix, quantity,
sales value, and discount are known, but before realized profit and fulfilment
outcomes are known. This makes the model a decision-support tool for identifying
orders whose known commercial terms are consistent with high profit, while
preventing the answer itself from entering the feature set.

## Candidate evidence

All calculations use the 100,000 cleaned order rows joined one-to-one to the
curated customer, product, and trusted state-region reference records. All three
labels have 100% availability. Numeric support is measured with point-biserial
correlation; categorical support is measured with Cramér's V. Statistical
significance alone is not treated as useful support at this sample size—the
effect magnitude must also be meaningful.

| Candidate | Operational definition used for scoring | Observed classes | Leakage-safe feature evidence |
|---|---|---:|---|
| High-Profit Order | `profit >= 5,363.845` (the fixed M4 P75) | 25,000 positive / 75,000 negative (**25.0000% / 75.0000%**) | `sales` has `r=0.587878`; `discount_pct` has `r=-0.228131`. Non-financial dimensions are negligible (largest tested Cramér's V `0.011435`). |
| High-Discount / Margin-Erosion | canonical M4 high-discount band (`discount_pct >= 38`) **and** low margin (`profit_margin_pct <= 10.79462548`, the observed P25) | 11,680 positive / 88,320 negative (**11.6800% / 88.3200%**) | After excluding `discount_pct`, `discount_band`, `sales`, `profit`, and `profit_margin_pct`, the strongest tested categorical association is sub-category at V `0.016871`; the largest numeric association is order month at `r=0.005464`. |
| Customer Segment | `Consumer` versus `Corporate` from curated customer data | 50,131 Consumer / 49,869 Corporate (**50.1310% / 49.8690%**) | Largest tested numeric association is `sales` at `r=0.005845`; largest categorical association is sub-category at V `0.013661`. The M3 category × segment test also found V `0.0080`, `p=0.2683`. |

The margin-erosion definition uses the already-bound M4 high-discount cutoff
and the corresponding lower-quartile rule for low margin. It is used here to
make the candidate measurable; it does not create a feature or model in M5.

## Scoring method

The original SRS §5.3 rubric is reused unchanged. Each criterion receives an
unweighted ordinal score from 1 (poor) to 5 (excellent), and the total is the
simple row sum. Availability reflects measured label coverage; balance reflects
the measured minority share; business value reflects an actionable retail
decision; feature support uses the leakage-safe effect sizes above; feasibility
accounts for label clarity, circularity/leakage risk, and the permitted
validation design.

| Candidate | Data availability | Class balance | Business value | Feature support | Feasibility | **Total** |
|---|---:|---:|---:|---:|---:|---:|
| **High-Profit Order Classification** | 5 | 4 | 5 | 5 | 5 | **24** |
| High-Discount / Margin-Erosion Classification | 5 | 3 | 5 | 1 | 2 | **16** |
| Customer Segment Classification | 5 | 5 | 1 | 1 | 5 | **17** |

### Score rationale

- **High-Profit Order:** full label coverage, a usable 25% positive class,
  direct value for pricing and profitability decisions, and two meaningful
  checkout-time signals make this both useful and technically feasible. Its
  defining outcome fields can be excluded cleanly.
- **High-Discount / Margin-Erosion:** the 11.68% class is trainable and the
  business problem is valuable, but every strong apparent relationship comes
  from fields that define the label. Once those circular inputs are removed,
  measured feature support is effectively zero, making a useful model doubtful.
- **Customer Segment:** the label is complete, almost perfectly balanced, and
  mechanically easy to validate. It has negligible measured support and little
  business value because Consumer/Corporate segment is already known before the
  transaction; prediction would duplicate an existing attribute.

The selected candidate leads the runner-up by seven points, so the SRS
within-one-point tie-break is not invoked.

## Retired candidates

- **Repeat Customer Prediction:** infeasible—**0 / 100,000** customers repeat,
  confirmed in M1.
- **Delayed Shipment Classification:** infeasible under the M4 gate. M3 found
  no meaningful predictor of `shipping_days`; creating a delay label would
  manufacture a class without defensible pre-outcome support.

Neither retired candidate is scored.

## Selected target contract

### Operational definition

- **Target column:** `is_high_profit_order`
- **Positive-class label:** `high_profit_order`
- **Negative-class label:** `standard_profit_order`
- **Positive rule:** `profit >= 5363.845`
- **Negative rule:** `profit < 5363.845`
- **Threshold provenance:** fixed P75 from the complete cleaned M4 profit
  distribution; it must be loaded from the governed feature contract and must
  not be recalculated independently by each consumer.

The positive class is `high_profit_order` because it is the business-actionable
outcome: it identifies orders whose commercial characteristics can inform
pricing, discount, category, and targeting decisions. Precision, recall, and F1
in the future M6 comparison must therefore be reported specifically for
`high_profit_order`, following the Addendum §22 principle. These labels are new
and do not reuse the retired satisfaction strings.

### Leakage and non-feature exclusions

The following fields must not enter model inputs:

- `profit`, `profit_margin_pct`, and `is_high_profit_order`, because they reveal
  or directly derive the target.
- `is_profit_outlier`, profit bands, margin-erosion flags, and any order-,
  customer-, category-, or mart-level profit aggregate computed from the current
  or future outcome.
- `ship_date` and `shipping_days`, because they occur after the checkout
  prediction point.
- `order_id`, `customer_id`, `product_id`, customer names, `product_name`, and
  postal code as predictive values; identifiers remain available only for audit
  and split verification.
- Raw `Year`, `Region`, `Ship Mode`, `Outlet Type`, `Country`, and `Postal Code`
  as predictive fields: M1–M3 established that they are decorative, unreliable,
  or non-predictive. This does not exclude the trusted state-derived region or
  the date-derived `order_year` feature.
- Any prediction, recommendation, future-order, or post-checkout aggregate.

`sales` and `discount_pct` are deliberately **permitted**. They are known at
checkout, neither is derived from the profit label, and their observed
associations are the principal leakage-safe support for this target. Their use
does not permit realized profit or margin back into the model.

### Validation Strategy

Use a reproducible **stratified random train/test split** at order-row grain,
stratified on `is_high_profit_order`, with the project-wide
`RANDOM_SEED=42`. The same immutable split and preprocessing must be used for
every algorithm in M6. No customer/product grouping or temporal cohort split is
required because every Customer ID and Product ID occurs exactly once and this
is an outcome-at-resolution target. The governing migration documents do not
bind a holdout percentage, so M5 does not invent one; it must be fixed once in
the authorized M6 training configuration before fitting any model.

## Business justification

High-Profit Order Classification is the strongest supported decision problem in
the migrated dataset. It converts a real measured outcome into an actionable
25% class, preserves a clear checkout-time prediction boundary, and retains
strong sales and discount signals after all profit-derived leakage is removed.
The alternative margin-erosion target becomes nearly signal-free when its own
defining inputs are excluded, while Customer Segment would predict information
the business already possesses. The decision therefore follows the measured M2
through M4 evidence rather than selecting a target by name or expectation.

## Phase gate

M5 creates this decision artifact only. No migrated model training,
preprocessing, feature pipeline, model registry entry, API activation, or
frontend change is authorized before explicit M6 approval. The existing
Olist-era ML implementation remains historical/retired migration context and
was not modified or executed in this phase.
