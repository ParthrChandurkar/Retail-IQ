# M1 Dataset Verification — Indian Store Data

This artifact records the empirical decisions that govern the M1 schema. Values
were computed from the downloaded `store_sales_data (2).csv`; they are not
inferred from the dataset description.

## Verified source facts

| Question | Empirical answer |
|---|---|
| Does Order ID repeat? | No. 100,000 rows contain 100,000 distinct Order IDs; maximum frequency 1. |
| Does Customer ID repeat? | No. 100,000 distinct Customer IDs; repeat-customer rate 0.0000%. |
| What is the 21st column? | `Sub-Category`. The actual file has 25 columns, not the advertised 20–21. |
| What is the date/null coverage? | Order Date 2019-01-01–2023-12-31; Ship Date 2019-01-02–2024-01-07; Sales Date 2019-01-01–2023-12-31. Ship Date, Discount, and Profit are each 0.0000% null. |
| What do Sales and Profit mean? | Sales is the INR purchase amount and Profit is profit after discount. Since every order occupies one row, both are complete transaction-line amounts. Sales is not a unit price; its correlation with Quantity is -0.002201, so a unit price cannot be recovered from it. |

## Schema consequences

- The source is a single order/line grain, so no `curated.order_items` table is
  created. Product, quantity, sales, discount, profit, and their outlier flags
  are stored on `curated.orders`.
- The source has no `price` field, so the folded flag is named
  `is_sales_outlier` rather than the inapplicable `is_price_outlier`.
- Customer identity does not repeat, so the former customer/customer-unique-ID
  split collapses to `customer_id`. Repeat-purchase analysis is empirically
  unsupported by this source.
- The source `Region` is retained as `region_as_reported` only. It is not a
  geographic grouping because all 10 states occur in all four values.

## Static reference provenance

- Coordinates are polygon centroids calculated from [DataMeet India state boundaries](https://github.com/datameet/maps/tree/b3fbbde595310b397a55d718e0958ce249a4fa1f/States), pinned to commit `b3fbbde595310b397a55d718e0958ce249a4fa1f` and licensed CC BY 4.0.
- Regions use the [Government of India Ministry of Housing and Urban Affairs regional classification](https://mohua.gov.in/upload/uploadfiles/files/4Empanelment_of_Resource.pdf). Its R1–R4 groups cover all 10 states represented by this dataset.
