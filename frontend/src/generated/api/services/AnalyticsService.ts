/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_dict_str__Any__ } from "../models/DataResponse_dict_str__Any__";
import type { DataResponse_list_dict_str__Any___ } from "../models/DataResponse_list_dict_str__Any___";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class AnalyticsService {
  /**
   * Correlation Matrix
   * @returns DataResponse_dict_str__Any__ Successful Response
   * @throws ApiError
   */
  public static correlationMatrixApiV1AnalyticsCorrelationMatrixGet({
    dateFrom,
    dateTo,
    state,
    city,
    category,
    sellerId,
    paymentType,
    customerSegment,
    reviewScoreMin,
    reviewScoreMax,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    state?: string | null;
    city?: string | null;
    category?: string | null;
    sellerId?: string | null;
    paymentType?: string | null;
    customerSegment?: string | null;
    reviewScoreMin?: number | null;
    reviewScoreMax?: number | null;
  }): CancelablePromise<DataResponse_dict_str__Any__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/correlation-matrix",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        state: state,
        city: city,
        category: category,
        seller_id: sellerId,
        payment_type: paymentType,
        customer_segment: customerSegment,
        review_score_min: reviewScoreMin,
        review_score_max: reviewScoreMax,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Hypothesis Tests
   * @returns DataResponse_list_dict_str__Any___ Successful Response
   * @throws ApiError
   */
  public static hypothesisTestsApiV1AnalyticsHypothesisTestsGet({
    dateFrom,
    dateTo,
    state,
    city,
    category,
    sellerId,
    paymentType,
    customerSegment,
    reviewScoreMin,
    reviewScoreMax,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    state?: string | null;
    city?: string | null;
    category?: string | null;
    sellerId?: string | null;
    paymentType?: string | null;
    customerSegment?: string | null;
    reviewScoreMin?: number | null;
    reviewScoreMax?: number | null;
  }): CancelablePromise<DataResponse_list_dict_str__Any___> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/hypothesis-tests",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        state: state,
        city: city,
        category: category,
        seller_id: sellerId,
        payment_type: paymentType,
        customer_segment: customerSegment,
        review_score_min: reviewScoreMin,
        review_score_max: reviewScoreMax,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Descriptive Stats
   * @returns DataResponse_list_dict_str__Any___ Successful Response
   * @throws ApiError
   */
  public static descriptiveStatsApiV1AnalyticsDescriptiveStatsGet({
    dateFrom,
    dateTo,
    state,
    city,
    category,
    sellerId,
    paymentType,
    customerSegment,
    reviewScoreMin,
    reviewScoreMax,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    state?: string | null;
    city?: string | null;
    category?: string | null;
    sellerId?: string | null;
    paymentType?: string | null;
    customerSegment?: string | null;
    reviewScoreMin?: number | null;
    reviewScoreMax?: number | null;
  }): CancelablePromise<DataResponse_list_dict_str__Any___> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/descriptive-stats",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        state: state,
        city: city,
        category: category,
        seller_id: sellerId,
        payment_type: paymentType,
        customer_segment: customerSegment,
        review_score_min: reviewScoreMin,
        review_score_max: reviewScoreMax,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Seasonality
   * @returns DataResponse_list_dict_str__Any___ Successful Response
   * @throws ApiError
   */
  public static seasonalityApiV1AnalyticsSeasonalityGet({
    dateFrom,
    dateTo,
    state,
    city,
    category,
    sellerId,
    paymentType,
    customerSegment,
    reviewScoreMin,
    reviewScoreMax,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    state?: string | null;
    city?: string | null;
    category?: string | null;
    sellerId?: string | null;
    paymentType?: string | null;
    customerSegment?: string | null;
    reviewScoreMin?: number | null;
    reviewScoreMax?: number | null;
  }): CancelablePromise<DataResponse_list_dict_str__Any___> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/seasonality",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        state: state,
        city: city,
        category: category,
        seller_id: sellerId,
        payment_type: paymentType,
        customer_segment: customerSegment,
        review_score_min: reviewScoreMin,
        review_score_max: reviewScoreMax,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
