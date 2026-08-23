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
    region,
    state,
    cityType,
    category,
    subCategory,
    segment,
    shipMode,
    orderValueTier,
    discountBand,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    region?: string | null;
    state?: string | null;
    cityType?: string | null;
    category?: string | null;
    subCategory?: string | null;
    segment?: string | null;
    shipMode?: string | null;
    orderValueTier?: string | null;
    discountBand?: string | null;
  }): CancelablePromise<DataResponse_dict_str__Any__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/correlation-matrix",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        region: region,
        state: state,
        city_type: cityType,
        category: category,
        sub_category: subCategory,
        segment: segment,
        ship_mode: shipMode,
        order_value_tier: orderValueTier,
        discount_band: discountBand,
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
    region,
    state,
    cityType,
    category,
    subCategory,
    segment,
    shipMode,
    orderValueTier,
    discountBand,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    region?: string | null;
    state?: string | null;
    cityType?: string | null;
    category?: string | null;
    subCategory?: string | null;
    segment?: string | null;
    shipMode?: string | null;
    orderValueTier?: string | null;
    discountBand?: string | null;
  }): CancelablePromise<DataResponse_list_dict_str__Any___> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/hypothesis-tests",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        region: region,
        state: state,
        city_type: cityType,
        category: category,
        sub_category: subCategory,
        segment: segment,
        ship_mode: shipMode,
        order_value_tier: orderValueTier,
        discount_band: discountBand,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Broad Screen
   * Expose the complete M3 categorical×numeric screen and field findings.
   * @returns DataResponse_dict_str__Any__ Successful Response
   * @throws ApiError
   */
  public static broadScreenApiV1AnalyticsBroadScreenGet({
    dateFrom,
    dateTo,
    region,
    state,
    cityType,
    category,
    subCategory,
    segment,
    shipMode,
    orderValueTier,
    discountBand,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    region?: string | null;
    state?: string | null;
    cityType?: string | null;
    category?: string | null;
    subCategory?: string | null;
    segment?: string | null;
    shipMode?: string | null;
    orderValueTier?: string | null;
    discountBand?: string | null;
  }): CancelablePromise<DataResponse_dict_str__Any__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/broad-screen",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        region: region,
        state: state,
        city_type: cityType,
        category: category,
        sub_category: subCategory,
        segment: segment,
        ship_mode: shipMode,
        order_value_tier: orderValueTier,
        discount_band: discountBand,
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
    region,
    state,
    cityType,
    category,
    subCategory,
    segment,
    shipMode,
    orderValueTier,
    discountBand,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    region?: string | null;
    state?: string | null;
    cityType?: string | null;
    category?: string | null;
    subCategory?: string | null;
    segment?: string | null;
    shipMode?: string | null;
    orderValueTier?: string | null;
    discountBand?: string | null;
  }): CancelablePromise<DataResponse_list_dict_str__Any___> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/descriptive-stats",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        region: region,
        state: state,
        city_type: cityType,
        category: category,
        sub_category: subCategory,
        segment: segment,
        ship_mode: shipMode,
        order_value_tier: orderValueTier,
        discount_band: discountBand,
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
    region,
    state,
    cityType,
    category,
    subCategory,
    segment,
    shipMode,
    orderValueTier,
    discountBand,
  }: {
    dateFrom?: string | null;
    dateTo?: string | null;
    region?: string | null;
    state?: string | null;
    cityType?: string | null;
    category?: string | null;
    subCategory?: string | null;
    segment?: string | null;
    shipMode?: string | null;
    orderValueTier?: string | null;
    discountBand?: string | null;
  }): CancelablePromise<DataResponse_list_dict_str__Any___> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/analytics/seasonality",
      query: {
        date_from: dateFrom,
        date_to: dateTo,
        region: region,
        state: state,
        city_type: cityType,
        category: category,
        sub_category: subCategory,
        segment: segment,
        ship_mode: shipMode,
        order_value_tier: orderValueTier,
        discount_band: discountBand,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
