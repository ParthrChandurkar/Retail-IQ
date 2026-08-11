/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CustomerRow = {
  customer_unique_id: string;
  first_order_ts: string | null;
  last_order_ts: string | null;
  order_count: number;
  total_spend: string;
  primary_state: string | null;
  primary_city: string | null;
  recency_score: number;
  frequency_score: number;
  monetary_score: number;
  rfm_segment: string;
  clv_historical: string;
};
