/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PredictionRequest = {
  /**
   * External order audit identifier
   */
  entity_id: string;
  /**
   * Checkout sales value in INR
   */
  sales: number;
  discount_pct: number;
  category: string;
  sub_category: string;
  segment: "Consumer" | "Corporate";
  city_type: "Tier 1" | "Tier 2" | "Village";
  state: string;
  /**
   * Trusted state_region_reference-derived region
   */
  region: "North" | "South" | "East" | "West";
  order_month: number;
  order_dow: number;
};
