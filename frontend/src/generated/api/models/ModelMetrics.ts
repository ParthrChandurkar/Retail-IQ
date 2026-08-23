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
  precision_high_profit_order: number;
  recall_high_profit_order: number;
  f1_high_profit_order: number;
  roc_auc: number;
  cv_f1_scores: Array<number>;
  cv_mean_f1_high_profit_order: number;
  cv_roc_auc_scores: Array<number>;
  cv_mean_roc_auc: number;
  confusion_matrix: Record<string, any>;
};
