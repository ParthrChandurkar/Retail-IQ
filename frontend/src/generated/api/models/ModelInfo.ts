/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GlobalFeature } from "./GlobalFeature";
export type ModelInfo = {
  model_id: number;
  target_variable: string;
  algorithm: string;
  trained_at: string;
  positive_class: string;
  negative_class: string;
  prediction_probability_semantics: string;
  feature_columns: Array<string>;
  top_global_features: Array<GlobalFeature>;
};
