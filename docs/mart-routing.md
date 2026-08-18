# Migration M2 Mart Routing Contract

This document records the authoritative mart for each future Indian Store Data API view. API router implementation is Migration M6; M2 establishes the data contract only.

## Revenue and KPI routing

| Request shape | Mart | Query aggregation | Rejected combinations |
|---|---|---|---|
| All-period KPI summary | `marts.kpi_snapshot` | Singleton | Every filter |
| Date-filtered KPI summary or revenue trend | `marts.revenue_daily` | Sum/range over `date` | Dimensional filters |
| Category/sub-category revenue trend | `marts.revenue_by_category` | Aggregate after category predicates | Geography, segment, ship mode |
| Region/state/city-type revenue trend | `marts.revenue_by_region` | Aggregate after geographic predicates | Category, segment, ship mode |

At most one dimensional filter family selects a revenue mart. Cross-family combinations are rejected rather than answered from a near-fact-grain cube.

## Domain routing

| Future view | Authoritative mart | Supported filters |
|---|---|---|
| Customer profiles and Order Value distribution | `marts.customer_profile` | order date, region, state, city type, given segment, order-value tier |
| Customer segmentation | `marts.customer_segments` | given segment, order-value tier, city type |
| Category/sub-category performance | `marts.revenue_by_category` | date, category, sub-category |
| Discount/profit analysis | `marts.category_discount_profit` | category, sub-category, discount band |
| Regional performance and state-centroid map | `marts.revenue_by_region` | date, trusted region, state, city type |
| Shipping-duration description | `marts.shipping_performance` | date, trusted region, ship mode |

There are no seller, payment, review, NLP, RFM, CLV, repeat-purchase, or individual-Product-ID mart routes in the migrated contract.

## Validation rules

- `date_from <= date_to`.
- A filter unsupported by the selected mart returns `400` with `code="unsupported_filter"` when M6 implements the routers.
- Region means the `state_region_reference` value. `region_as_reported` is audit-only and is never routed as geography.
- State-centroid latitude/longitude are presentation coordinates, not customer-level geolocation.
- Customer counts are non-additive; exact filtered distinct counts must not be reconstructed by summing daily distinct counts.
- Shipping duration is retained for transparent description, but the M2 integrity check found no credible ordering by ship mode. It cannot define delayed shipment unless M4 establishes an independently valid baseline.
