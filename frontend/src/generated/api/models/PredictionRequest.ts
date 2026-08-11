/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PredictionRequest = {
  /**
   * Order or external audit identifier
   */
  entity_id: string;
  total_price: number;
  total_freight: number;
  item_count: number;
  product_count: number;
  seller_count: number;
  average_item_price: number;
  maximum_item_price: number;
  freight_ratio?: number | null;
  payment_value?: number | null;
  payment_installments?: number | null;
  delivery_days?: number | null;
  delivery_delay_hours?: number | null;
  is_late?: number | null;
  approval_hours?: number | null;
  carrier_handling_hours?: number | null;
  estimated_delivery_days?: number | null;
  shipping_limit_slack_days?: number | null;
  seller_distance_km?: number | null;
  average_product_weight_g?: number | null;
  average_product_volume_cm3?: number | null;
  customer_state: string;
  seller_state: string;
  dominant_category: string;
  primary_payment_type: string;
  purchase_month: number;
  purchase_weekday: number;
  purchase_hour: number;
};
