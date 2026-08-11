/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_GlobalFeature__ } from "../models/DataResponse_list_GlobalFeature__";
import type { DataResponse_ModelInfo_ } from "../models/DataResponse_ModelInfo_";
import type { DataResponse_ModelMetrics_ } from "../models/DataResponse_ModelMetrics_";
import type { DataResponse_PredictionResult_ } from "../models/DataResponse_PredictionResult_";
import type { PredictionRequest } from "../models/PredictionRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class ClassificationService {
  /**
   * Model Info
   * @returns DataResponse_ModelInfo_ Successful Response
   * @throws ApiError
   */
  public static modelInfoApiV1ClassificationModelInfoGet(): CancelablePromise<DataResponse_ModelInfo_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/classification/model-info",
    });
  }
  /**
   * Model Metrics
   * @returns DataResponse_ModelMetrics_ Successful Response
   * @throws ApiError
   */
  public static modelMetricsApiV1ClassificationMetricsGet(): CancelablePromise<DataResponse_ModelMetrics_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/classification/metrics",
    });
  }
  /**
   * Feature Importance
   * @returns DataResponse_list_GlobalFeature__ Successful Response
   * @throws ApiError
   */
  public static featureImportanceApiV1ClassificationFeatureImportanceGet(): CancelablePromise<DataResponse_list_GlobalFeature__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/classification/feature-importance",
    });
  }
  /**
   * Predict
   * @returns DataResponse_PredictionResult_ Successful Response
   * @throws ApiError
   */
  public static predictApiV1ClassificationPredictPost({
    requestBody,
  }: {
    requestBody: PredictionRequest;
  }): CancelablePromise<DataResponse_PredictionResult_> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/classification/predict",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
