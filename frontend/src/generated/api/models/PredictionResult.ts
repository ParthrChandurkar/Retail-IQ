/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GlobalFeature } from "./GlobalFeature";
export type PredictionResult = {
  model_id: number;
  target_variable: string;
  predicted_label: "high_profit_order" | "standard_profit_order";
  /**
   * Confidence in predicted_label, not a fixed-class probability
   */
  predicted_probability: number;
  /**
   * Model-level importance shared by predictions from this model
   */
  top_global_features: Array<GlobalFeature>;
};
