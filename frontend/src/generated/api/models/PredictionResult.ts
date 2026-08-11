/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GlobalFeature } from "./GlobalFeature";
export type PredictionResult = {
  model_id: number;
  target_variable: string;
  predicted_label: "low_satisfaction" | "high_satisfaction";
  predicted_probability: number;
  /**
   * Model-level importance; identical for every prediction from this model.
   */
  top_global_features: Array<GlobalFeature>;
};
