# Power BI Integration

Retail IQ exposes its finalized PostgreSQL marts to Power BI through the
least-privilege `powerbi_reader` login. The role can select from `marts` only;
it cannot use `raw`, `curated`, or `ml`.

## Prerequisites and connection

1. Set a strong unique `POWERBI_READER_PASSWORD` in `backend/.env` before the
   first `docker compose up -d`. Never commit that value.
2. Complete the README setup through `make analytics-reports` so the marts are
   populated.
3. In Power BI Desktop choose **Get data → PostgreSQL database**.
4. Enter:

| Setting | Local reference value |
|---|---|
| Server | `localhost:5432` |
| Database | `retail_bi` |
| Data connectivity mode | `Import` |
| Authentication | Database |
| User name | `powerbi_reader` |
| Password | the local `POWERBI_READER_PASSWORD` value |

Import is recommended: the source is a bounded academic dataset, marts are
pre-aggregated, and batch refresh controls freshness. Use DirectQuery only when
a stakeholder explicitly needs on-demand database freshness and accepts its
latency/availability trade-off. No Microsoft, Azure AD, or Power BI Service
credential is needed for the local Desktop connection.

## Tables and final grains

Import these tables from the `marts` schema:

| Table | Final grain / key |
|---|---|
| `kpi_snapshot` | singleton (`snapshot_id = 1`) |
| `revenue_daily` | `date` |
| `revenue_by_category` | `date × category` |
| `revenue_by_region` | `date × state × city` |
| `seller_performance` | `date × seller_id` |
| `payment_method_mix` | `date × payment_type` |
| `customer_profile` | `customer_unique_id` |
| `customer_segments` | `segment` |
| `delivery_performance` | governed multi-filter delivery aggregate |
| `review_summary` | governed multi-filter review aggregate |

These are the post-refactor physical grains. Do not widen or join the five
primary revenue facts to one another: that creates fact-to-fact multiplication.

## Model relationships

Create the `Date` table from the first expression in
[`powerbi/RetailIQ-Measures.dax`](../powerbi/RetailIQ-Measures.dax), mark it as
the date table, and add single-direction one-to-many relationships:

| One side | Many side | Cardinality / direction |
|---|---|---|
| `Date[Date]` | `revenue_daily[date]` | 1:*; Date filters fact |
| `Date[Date]` | `revenue_by_category[date]` | 1:*; Date filters fact |
| `Date[Date]` | `revenue_by_region[date]` | 1:*; Date filters fact |
| `Date[Date]` | `seller_performance[date]` | 1:*; Date filters fact |
| `Date[Date]` | `payment_method_mix[date]` | 1:*; Date filters fact |
| `customer_segments[segment]` | `customer_profile[rfm_segment]` | 1:*; segment filters profile |

Keep `kpi_snapshot` disconnected. `delivery_performance` and `review_summary`
carry multiple dimension combinations and should initially remain standalone;
use their own fields on their report pages. This avoids ambiguous filter paths.

## Governed DAX measures

Copy the complete library from
[`powerbi/RetailIQ-Measures.dax`](../powerbi/RetailIQ-Measures.dax). It directly
implements Addendum §7:

- Revenue is the sum of delivered-order item price plus freight already stored
  in `revenue_daily[revenue]`.
- AOV is revenue divided by delivered-order count in the same context.
- MoM and YoY compare calendar periods through the purchase-date axis.
- CLV is historical `customer_profile[total_spend]`, labeled “Lifetime Value
  (to date)” and never presented as a forecast.
- Customer Count counts rows in the one-row-per-customer `customer_profile`, so
  it is an exact distinct delivered-customer count and responds to customer
  segment/geography filters. It deliberately returns blank under a Date filter
  because summing daily distinct counts would double-count repeat customers. The
  web API can compute date-filtered distinct customers from curated order
  linkage, but the least-privilege Power BI role cannot access curated data. This
  guard preserves the binding definition instead of displaying a fabricated
  filtered number.

### Showing cleaning and preprocessing progress

Add a **Data Quality & Pipeline** report page using the checked-in, generated
[`pre-clean`](../analytics/reports/data_quality_report_pre_clean.md) and
[`post-clean`](../analytics/reports/data_quality_report_post_clean.md) reports as
the governed evidence source. Show the raw/curated row-count reconciliation,
invalid-row handling, geolocation enrichment gaps, duplicate-review consistency,
and retained outlier flags. These results are generated from the dataset during
`make etl`; do not type substitute values or infer missing demographics. Power BI
reads only marts by design, so the quality evidence remains a documented refresh
snapshot rather than granting the BI login access to raw/curated records.

Format Revenue, AOV, and CLV as BRL; format growth as Percentage.

## Reconciliation evidence

The Phase 9 spot-check used the populated database and the unfiltered live
dashboard:

| KPI | Web dashboard / `kpi_snapshot` | DAX source calculation | Result |
|---|---:|---:|---|
| Revenue | R$ 15,419,773.75 | `SUM(revenue_daily[revenue])` = R$ 15,419,773.75 | exact |
| AOV | R$ 159.826838761… | Revenue ÷ 96,478 delivered orders = R$ 159.826838761… | exact |

The UI rounds AOV to R$ 159.83. Re-run these SQL checks after a refresh:

```sql
SELECT total_revenue, total_orders, average_order_value
FROM marts.kpi_snapshot WHERE snapshot_id = 1;

SELECT SUM(revenue), SUM(order_count), SUM(revenue) / SUM(order_count)
FROM marts.revenue_daily;
```

## Refresh and report construction

After `make etl && make analytics-reports`, choose **Refresh** in Power BI
Desktop. Recommended pages are Executive KPIs, Revenue & Categories, Regional,
Sellers & Payments, and Customer Value. Use only the matching fact table on
each page and the shared Date dimension.

Power BI Desktop is installed software, but a valid `.pbix`/`.pbit` requires GUI
authoring and is not safely generated as a text artifact. This repository does
not include a fake template. The tested database access, final-grain model,
relationships, and DAX library are the reproducible integration deliverable.
