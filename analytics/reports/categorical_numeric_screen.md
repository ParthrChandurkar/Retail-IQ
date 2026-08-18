# Categorical × Numeric Screen

- **Generated at:** `2026-08-18T16:23:03.258209+00:00`
- **Code/commit reference:** `840a796`
- **Dataset row counts used:** customers=100,000, customer_profile=100,000, orders=100,000, raw_transactions=100,000, products=100,000
- **Metric contract:** all curated orders; Revenue=`SUM(sales)`, Profit=`SUM(profit)`, date axis=`order_date`, currency=INR.


## Result first

`outlet_type` is the newly identified fourth decorative field. `country` is constant metadata, while `postal_code` is a redundant State proxy. The previously identified `region_as_reported`, `year_as_reported`, and `ship_mode` remain decorative. No comparison survived full-screen FDR correction with a material effect size. The specification-designated State, City Type, Segment, Category, Sub-Category, trusted Region, and order-year dimensions remain valid descriptive groupings, but the screen does not support causal or performance-difference claims for them.

## Field-level summary

| Field | Groups | Maximum effect | Any FDR significant | Classification |
|---|---|---|---|---|
| outlet_type | 3 | 1.8602e-05 | False | decorative |
| city_type | 3 | 1.2739e-05 | False | valid_dimension_no_material_numeric_effect |
| category | 6 | 3.1635e-05 | False | valid_dimension_no_material_numeric_effect |
| region_as_reported | 4 | 9.7267e-05 | False | decorative |
| country | 1 | 0.0000 | False | constant_metadata |
| segment | 2 | 3.4164e-05 | False | valid_dimension_no_material_numeric_effect |
| ship_mode | 4 | 3.2881e-05 | False | decorative |
| state | 10 | 0.0001 | False | valid_dimension_no_material_numeric_effect |
| postal_code | 10 | 0.0001 | False | redundant_state_proxy |
| sub_category | 24 | 0.0003 | False | valid_dimension_no_material_numeric_effect |
| trusted_region | 4 | 0.0001 | False | valid_dimension_no_material_numeric_effect |
| year_as_reported | 5 | 8.3560e-05 | False | decorative |
| order_year | 5 | 5.5850e-05 | False | valid_dimension_no_material_numeric_effect |

## Complete 13 × 6 screen

| Categorical field | Numeric outcome | Groups | ANOVA F | ANOVA p | ANOVA FDR q | η² | Kruskal H | Kruskal p | Kruskal FDR q | ε² |
|---|---|---|---|---|---|---|---|---|---|---|
| outlet_type | sales | 3 | 0.1361 | 0.8727 | 0.9996 | 2.7226e-06 | 0.2673 | 0.8749 | 0.9996 | 0.0000 |
| outlet_type | profit | 3 | 0.4863 | 0.6149 | 0.9996 | 9.7262e-06 | 0.1322 | 0.9360 | 0.9996 | 0.0000 |
| outlet_type | discount_pct | 3 | 0.5428 | 0.5811 | 0.9996 | 1.0857e-05 | 1.0851 | 0.5813 | 0.9996 | 0.0000 |
| outlet_type | quantity | 3 | 0.0692 | 0.9331 | 0.9996 | 1.3840e-06 | 0.1379 | 0.9334 | 0.9996 | 0.0000 |
| outlet_type | shipping_days | 3 | 0.0148 | 0.9853 | 0.9996 | 2.9620e-07 | 0.0298 | 0.9852 | 0.9996 | 0.0000 |
| outlet_type | profit_margin_pct | 3 | 0.9301 | 0.3945 | 0.9996 | 1.8602e-05 | 2.0517 | 0.3585 | 0.9996 | 5.1676e-07 |
| city_type | sales | 3 | 0.0711 | 0.9314 | 0.9996 | 1.4215e-06 | 0.1473 | 0.9290 | 0.9996 | 0.0000 |
| city_type | profit | 3 | 0.2650 | 0.7672 | 0.9996 | 5.3010e-06 | 0.7980 | 0.6710 | 0.9996 | 0.0000 |
| city_type | discount_pct | 3 | 0.1625 | 0.8500 | 0.9996 | 3.2503e-06 | 0.3246 | 0.8502 | 0.9996 | 0.0000 |
| city_type | quantity | 3 | 0.0491 | 0.9521 | 0.9996 | 9.8111e-07 | 0.0992 | 0.9516 | 0.9996 | 0.0000 |
| city_type | shipping_days | 3 | 0.0644 | 0.9376 | 0.9996 | 1.2886e-06 | 0.1314 | 0.9364 | 0.9996 | 0.0000 |
| city_type | profit_margin_pct | 3 | 0.6369 | 0.5289 | 0.9996 | 1.2739e-05 | 2.1918 | 0.3342 | 0.9996 | 1.9183e-06 |
| category | sales | 6 | 0.5522 | 0.7368 | 0.9996 | 2.7611e-05 | 2.7717 | 0.7351 | 0.9996 | 0.0000 |
| category | profit | 6 | 0.2140 | 0.9567 | 0.9996 | 1.0701e-05 | 0.9042 | 0.9699 | 0.9996 | 0.0000 |
| category | discount_pct | 6 | 0.5102 | 0.7688 | 0.9996 | 2.5513e-05 | 2.5654 | 0.7666 | 0.9996 | 0.0000 |
| category | quantity | 6 | 0.5352 | 0.7498 | 0.9996 | 2.6759e-05 | 2.6860 | 0.7483 | 0.9996 | 0.0000 |
| category | shipping_days | 6 | 0.0932 | 0.9933 | 0.9996 | 4.6606e-06 | 0.4692 | 0.9932 | 0.9996 | 0.0000 |
| category | profit_margin_pct | 6 | 0.6327 | 0.6748 | 0.9996 | 3.1635e-05 | 3.4161 | 0.6361 | 0.9996 | 0.0000 |
| region_as_reported | sales | 4 | 3.2424 | 0.0210 | 0.4770 | 9.7267e-05 | 9.7320 | 0.0210 | 0.3880 | 6.7323e-05 |
| region_as_reported | profit | 4 | 3.1157 | 0.0250 | 0.4770 | 9.3466e-05 | 7.0111 | 0.0715 | 0.6152 | 4.0112e-05 |
| region_as_reported | discount_pct | 4 | 0.8754 | 0.4529 | 0.9996 | 2.6264e-05 | 2.6495 | 0.4489 | 0.9996 | 0.0000 |
| region_as_reported | quantity | 4 | 1.6593 | 0.1734 | 0.8119 | 4.9778e-05 | 4.9818 | 0.1731 | 0.7552 | 1.9819e-05 |
| region_as_reported | shipping_days | 4 | 2.0100 | 0.1102 | 0.6988 | 6.0297e-05 | 6.0112 | 0.1111 | 0.6152 | 3.0113e-05 |
| region_as_reported | profit_margin_pct | 4 | 1.4091 | 0.2379 | 0.8803 | 4.2273e-05 | 4.1631 | 0.2444 | 0.8835 | 1.1632e-05 |
| country | sales | 1 | — | — | — | 0.0000 | — | — | — | 0.0000 |
| country | profit | 1 | — | — | — | 0.0000 | — | — | — | 0.0000 |
| country | discount_pct | 1 | — | — | — | 0.0000 | — | — | — | 0.0000 |
| country | quantity | 1 | — | — | — | 0.0000 | — | — | — | 0.0000 |
| country | shipping_days | 1 | — | — | — | 0.0000 | — | — | — | 0.0000 |
| country | profit_margin_pct | 1 | — | — | — | 0.0000 | — | — | — | 0.0000 |
| segment | sales | 2 | 3.4165 | 0.0646 | 0.6988 | 3.4164e-05 | 3.4090 | 0.0648 | 0.6152 | 2.4091e-05 |
| segment | profit | 2 | 1.3080 | 0.2528 | 0.8803 | 1.3081e-05 | 2.6191 | 0.1056 | 0.6152 | 1.6191e-05 |
| segment | discount_pct | 2 | 0.3396 | 0.5601 | 0.9996 | 3.3959e-06 | 0.3467 | 0.5560 | 0.9996 | 0.0000 |
| segment | quantity | 2 | 1.3312 | 0.2486 | 0.8803 | 1.3312e-05 | 1.3293 | 0.2489 | 0.8835 | 3.2927e-06 |
| segment | shipping_days | 2 | 0.6151 | 0.4329 | 0.9996 | 6.1513e-06 | 0.6195 | 0.4312 | 0.9996 | 0.0000 |
| segment | profit_margin_pct | 2 | 0.4262 | 0.5139 | 0.9996 | 4.2622e-06 | 0.4249 | 0.5145 | 0.9996 | 0.0000 |
| ship_mode | sales | 4 | 0.1927 | 0.9015 | 0.9996 | 5.7801e-06 | 0.5787 | 0.9013 | 0.9996 | 0.0000 |
| ship_mode | profit | 4 | 0.2176 | 0.8842 | 0.9996 | 6.5295e-06 | 0.9609 | 0.8107 | 0.9996 | 0.0000 |
| ship_mode | discount_pct | 4 | 0.4937 | 0.6866 | 0.9996 | 1.4812e-05 | 1.4765 | 0.6877 | 0.9996 | 0.0000 |
| ship_mode | quantity | 4 | 0.5183 | 0.6697 | 0.9996 | 1.5550e-05 | 1.5493 | 0.6709 | 0.9996 | 0.0000 |
| ship_mode | shipping_days | 4 | 1.0960 | 0.3493 | 0.9996 | 3.2881e-05 | 3.2957 | 0.3482 | 0.9996 | 2.9573e-06 |
| ship_mode | profit_margin_pct | 4 | 0.2508 | 0.8608 | 0.9996 | 7.5238e-06 | 0.6909 | 0.8753 | 0.9996 | 0.0000 |
| state | sales | 10 | 1.6030 | 0.1079 | 0.6988 | 0.0001 | 14.4135 | 0.1084 | 0.6152 | 5.4140e-05 |
| state | profit | 10 | 1.5979 | 0.1094 | 0.6988 | 0.0001 | 18.9060 | 0.0260 | 0.3880 | 9.9070e-05 |
| state | discount_pct | 10 | 0.8809 | 0.5414 | 0.9996 | 7.9284e-05 | 7.9257 | 0.5416 | 0.9996 | 0.0000 |
| state | quantity | 10 | 0.4391 | 0.9145 | 0.9996 | 3.9523e-05 | 3.9512 | 0.9146 | 0.9996 | 0.0000 |
| state | shipping_days | 10 | 0.7319 | 0.6800 | 0.9996 | 6.5873e-05 | 6.5683 | 0.6820 | 0.9996 | 0.0000 |
| state | profit_margin_pct | 10 | 0.8621 | 0.5586 | 0.9996 | 7.7595e-05 | 9.4428 | 0.3974 | 0.9996 | 4.4282e-06 |
| postal_code | sales | 10 | 1.6030 | 0.1079 | 0.6988 | 0.0001 | 14.4135 | 0.1084 | 0.6152 | 5.4140e-05 |
| postal_code | profit | 10 | 1.5979 | 0.1094 | 0.6988 | 0.0001 | 18.9060 | 0.0260 | 0.3880 | 9.9070e-05 |
| postal_code | discount_pct | 10 | 0.8809 | 0.5414 | 0.9996 | 7.9284e-05 | 7.9257 | 0.5416 | 0.9996 | 0.0000 |
| postal_code | quantity | 10 | 0.4391 | 0.9145 | 0.9996 | 3.9523e-05 | 3.9512 | 0.9146 | 0.9996 | 0.0000 |
| postal_code | shipping_days | 10 | 0.7319 | 0.6800 | 0.9996 | 6.5873e-05 | 6.5683 | 0.6820 | 0.9996 | 0.0000 |
| postal_code | profit_margin_pct | 10 | 0.8621 | 0.5586 | 0.9996 | 7.7595e-05 | 9.4428 | 0.3974 | 0.9996 | 4.4282e-06 |
| sub_category | sales | 24 | 0.6775 | 0.8726 | 0.9996 | 0.0002 | 15.6023 | 0.8718 | 0.9996 | 0.0000 |
| sub_category | profit | 24 | 0.5555 | 0.9567 | 0.9996 | 0.0001 | 14.2824 | 0.9185 | 0.9996 | 0.0000 |
| sub_category | discount_pct | 24 | 1.3304 | 0.1330 | 0.7368 | 0.0003 | 30.6455 | 0.1318 | 0.6518 | 7.6474e-05 |
| sub_category | quantity | 24 | 0.4167 | 0.9936 | 0.9996 | 9.5863e-05 | 9.5949 | 0.9935 | 0.9996 | 0.0000 |
| sub_category | shipping_days | 24 | 0.8089 | 0.7238 | 0.9996 | 0.0002 | 18.6012 | 0.7241 | 0.9996 | 0.0000 |
| sub_category | profit_margin_pct | 24 | 1.2608 | 0.1804 | 0.8119 | 0.0003 | 29.0609 | 0.1783 | 0.7552 | 6.0623e-05 |
| trusted_region | sales | 4 | 3.0736 | 0.0265 | 0.4770 | 9.2204e-05 | 9.1837 | 0.0269 | 0.3880 | 6.1840e-05 |
| trusted_region | profit | 4 | 3.5092 | 0.0146 | 0.4770 | 0.0001 | 12.8610 | 0.0049 | 0.3562 | 9.8614e-05 |
| trusted_region | discount_pct | 4 | 0.7437 | 0.5258 | 0.9996 | 2.2312e-05 | 2.2352 | 0.5251 | 0.9996 | 0.0000 |
| trusted_region | quantity | 4 | 0.2149 | 0.8861 | 0.9996 | 6.4474e-06 | 0.6439 | 0.8863 | 0.9996 | 0.0000 |
| trusted_region | shipping_days | 4 | 1.3480 | 0.2567 | 0.8803 | 4.0441e-05 | 4.0353 | 0.2577 | 0.8835 | 1.0354e-05 |
| trusted_region | profit_margin_pct | 4 | 1.7498 | 0.1544 | 0.7942 | 5.2494e-05 | 5.5479 | 0.1358 | 0.6518 | 2.5480e-05 |
| year_as_reported | sales | 5 | 2.0891 | 0.0794 | 0.6988 | 8.3560e-05 | 8.3505 | 0.0796 | 0.6152 | 4.3507e-05 |
| year_as_reported | profit | 5 | 1.8486 | 0.1165 | 0.6988 | 7.3941e-05 | 8.2057 | 0.0843 | 0.6152 | 4.2059e-05 |
| year_as_reported | discount_pct | 5 | 0.0141 | 0.9996 | 0.9996 | 5.6257e-07 | 0.0556 | 0.9996 | 0.9996 | 0.0000 |
| year_as_reported | quantity | 5 | 0.1479 | 0.9640 | 0.9996 | 5.9164e-06 | 0.5884 | 0.9643 | 0.9996 | 0.0000 |
| year_as_reported | shipping_days | 5 | 0.7751 | 0.5412 | 0.9996 | 3.1004e-05 | 3.0979 | 0.5416 | 0.9996 | 0.0000 |
| year_as_reported | profit_margin_pct | 5 | 0.6505 | 0.6265 | 0.9996 | 2.6022e-05 | 1.6611 | 0.7978 | 0.9996 | 0.0000 |
| order_year | sales | 5 | 0.0650 | 0.9922 | 0.9996 | 2.6020e-06 | 0.2618 | 0.9921 | 0.9996 | 0.0000 |
| order_year | profit | 5 | 0.0845 | 0.9872 | 0.9996 | 3.3791e-06 | 0.4482 | 0.9783 | 0.9996 | 0.0000 |
| order_year | discount_pct | 5 | 1.0841 | 0.3624 | 0.9996 | 4.3364e-05 | 4.3250 | 0.3638 | 0.9996 | 3.2503e-06 |
| order_year | quantity | 5 | 0.2796 | 0.8914 | 0.9996 | 1.1183e-05 | 1.1187 | 0.8913 | 0.9996 | 0.0000 |
| order_year | shipping_days | 5 | 1.3963 | 0.2324 | 0.8803 | 5.5850e-05 | 5.5878 | 0.2321 | 0.8835 | 1.5879e-05 |
| order_year | profit_margin_pct | 5 | 0.3382 | 0.8524 | 0.9996 | 1.3527e-05 | 1.7743 | 0.7772 | 0.9996 | 0.0000 |

## Method and exclusions

One-way ANOVA and Kruskal-Wallis for all field/outcome pairs; Benjamini-Hochberg FDR correction within the complete screen. Effect sizes are eta-squared and epsilon-squared. Practical association screening uses 0.01 as the small-effect boundary; statistical significance alone is not treated as business importance.

Customer/Order/Product IDs, names, product name and date of birth are identifiers or PII; dates are handled as time dimensions.
