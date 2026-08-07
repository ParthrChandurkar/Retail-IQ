# Retail IQ faculty progress dashboard

## Page 1 — Executive overview

- Cards: Delivered Revenue, Delivered Orders, Customers, AOV, Repeat Customer Rate.
- Line chart: `monthly_revenue[month]` vs `monthly_revenue[revenue_brl]`.
- Phase status table: phase, name, status, evidence.

## Page 2 — Data quality and preprocessing

- Pipeline callout: nine CSV sources → raw tables → curated entities → analytics marts.
- Bar chart: `curated_row_counts[table]` vs rows.
- Matrix: cleaning source, raw rows, curated rows, removed rows, rationale.
- Outlier chart: global and persisted flag counts. The accompanying text must say that legitimate outliers were retained and flagged, not deleted.

## Page 3 — Customer analytics

- Segment bar chart: segment vs customers.
- CLV chart: segment vs average historical CLV.
- Cards: customer count, repeat-customer rate, average CLV.

## Page 4 — Statistical evidence

- Test cards/table: comparison, statistic, p-value, significant, conclusion.
- Callout: late deliveries average 2.5665 reviews versus 4.2937 for on-time deliveries.

All visuals are based on the generated extracts. Phase 4 and later work must remain visibly pending until its governed artifact exists.
