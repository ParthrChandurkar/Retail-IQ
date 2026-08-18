# Retail IQ — Dataset Migration Addendum v2.2
## Customer & Product Analytics Redesign — Zero-Repetition Finding

**Relationship to prior documents:** extends `SRS-Migration-Addendum-v2.1.md`, which extends v2.0 and the v1.x/SRS.md chain. Resolves a strategic-scope finding from M1: this dataset has no repeating entities at the individual Customer ID (confirmed) or Product ID (pending one-line confirmation, see below) level. Updated authority order:

1. **This document (v2.2)**
2. SRS-Migration-Addendum-v2.1.md
3. SRS-Migration-Addendum-v2.0.md
4. SRS-Clarifications-Addendum-v1.4.md through v1.1
5. SRS.md v1.0
6. No undocumented assumptions

---

### Finding

M1 confirmed **0.0000% repeat-customer rate** — 100,000 unique Customer IDs across 100,000 orders. No customer in this dataset ever places a second order. `curated.products` is also reported at 100,000 rows, which strongly suggests Product ID follows the identical pattern (consistent with the source listing's own note that product names were randomly generated) — **M2 must state this explicitly as a confirmed number**, not leave it implied by a row count.

**Implication:** this dataset has no genuine repeat-entity behavior to analyze at the individual Customer ID or Product ID level. Every meaningful analysis must operate either at the **categorical/dimensional level** (Segment, City Type, Region, State, Category, Sub-Category, Ship Mode) or at the **single-transaction level** (order value, profit, discount) — not the longitudinal, per-entity level the original Olist-based design assumed throughout.

### Resolution (binding — supersedes the relevant parts of Migration Addendum v2.0 §3, §8, §9)

**1. Repeat Customer Prediction candidate — retired, not scored.** A 0% positive-class base rate is not a weak candidate, it's an undefined one — there are no positive examples to learn from or evaluate against. Do not include it in the Migration Phase M5 scoring exercise. Document its exclusion with one line ("infeasible: 0/100,000 repeat customers, confirmed in M1") rather than silently dropping it or spending effort scoring something mathematically impossible.

**2. `customer_profile` mart redesigned as a cross-sectional profile, not a behavioral one.** RFM's "Frequency" dimension is degenerate (always 1) and must not be presented as a real segmentation axis. New shape: `order_value, profit, discount_pct, segment, city_type, region (state_region_reference-derived), state`. "Recency" may still carry meaning if there's a reason to track it (order dates do vary across customers); "Frequency" and "Monetary-over-time" do not, and should be dropped rather than faked.

**3. "Customer Lifetime Value" terminology is retired for this dataset.** It cannot mean anything beyond a single order's value here, and continuing to call it "CLV" would overclaim what the data supports — the same overclaiming the original project already refused to do for Olist's *historical* CLV framing (SRS §12.3), just a stricter version of the same discipline now that even "historical, single-period" framing doesn't apply. Rename every reference to **"Order Value."**

**4. Customer segmentation replaces RFM scoring with what the data actually supports.** Cross-tabulate the *given* `segment` (Consumer/Corporate) against order-value tiers (e.g. quartiles) and/or `city_type`. This still delivers genuine, presentable segmentation analytics — it's just built on dimensions that are real in this dataset instead of forcing a behavioral framework (RFM) onto data that can't support it.

**5. Product analytics pivots to Category/Sub-Category.** Migration Phase M2 must explicitly confirm and state the Product ID repetition rate. If confirmed near-zero (expected): no "top products by repeat sales" panel, no individual-Product-ID analytics of any kind — all product-level analysis operates at the 6-category / sub-category level, which *does* repeat and *is* analytically meaningful.

**6. High-Profit Order/Customer Classification is unaffected and remains fully viable** — it's a single-transaction classification, not a behavioral one. It becomes relatively more central among the M5 candidates now that Repeat Customer is off the table.

**7. Proactive check for M2/M3.** Two fields have now been found to not encode what their names imply (`Region` vs. `State`; `Year` vs. `Order Date`, 80% disagreement). Before `shipping_days` is used for anything — including the eventual delayed-shipment feature in M4 — explicitly verify whether it actually correlates with `ship_mode` as expected (Same Day / First Class should show shorter durations than Standard Class). Don't assume the third categorical field is trustworthy just because it hasn't been disproven yet.

---

*M2 may proceed under this redesign. State the Product ID repetition rate explicitly in the M2 report — this document's assumption should be confirmed, not left inherited.*
