/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_DashboardSummary_ } from "../models/DataResponse_DashboardSummary_";
import type { DataResponse_list_PerformanceRow__ } from "../models/DataResponse_list_PerformanceRow__";
import type { DataResponse_list_RevenuePoint__ } from "../models/DataResponse_list_RevenuePoint__";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class DashboardService {
  /**
   * Summary
   * @returns DataResponse_DashboardSummary_ Successful Response
   * @throws ApiError
   */
  public static summaryApiV1DashboardSummaryGet({
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
  }): CancelablePromise<DataResponse_DashboardSummary_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/summary",
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
   * Revenue Trend
   * @returns DataResponse_list_RevenuePoint__ Successful Response
   * @throws ApiError
   */
  public static revenueTrendApiV1DashboardRevenueTrendGet({
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
  }): CancelablePromise<DataResponse_list_RevenuePoint__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/revenue-trend",
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
   * Top Categories
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static topCategoriesApiV1DashboardTopCategoriesGet({
    limit = 10,
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
    limit?: number;
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
  }): CancelablePromise<DataResponse_list_PerformanceRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/top-categories",
      query: {
        limit: limit,
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
