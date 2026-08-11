/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ModelMetrics = {
  model_id: number;
  algorithm: string;
  positive_class: string;
  negative_class: string;
  accuracy: number;
  precision_low_satisfaction: number;
  recall_low_satisfaction: number;
  f1_low_satisfaction: number;
  roc_auc: number;
  cv_f1_scores: Array<number>;
  cv_mean_f1_low_satisfaction: number;
  cv_roc_auc_scores: Array<number>;
  cv_mean_roc_auc: number;
  confusion_matrix: Record<string, any>;
};
