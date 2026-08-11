/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_DashboardSummary_ } from "../models/DataResponse_DashboardSummary_";
import type { DataResponse_list_PerformanceRow__ } from "../models/DataResponse_list_PerformanceRow__";
import type { DataResponse_list_ProductDetail__ } from "../models/DataResponse_list_ProductDetail__";
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
  }): CancelablePromise<DataResponse_DashboardSummary_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/summary",
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
   * Revenue Trend
   * @returns DataResponse_list_RevenuePoint__ Successful Response
   * @throws ApiError
   */
  public static revenueTrendApiV1DashboardRevenueTrendGet({
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
  }): CancelablePromise<DataResponse_list_RevenuePoint__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/revenue-trend",
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
   * Top Categories
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static topCategoriesApiV1DashboardTopCategoriesGet({
    limit = 10,
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
    limit?: number;
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
  }): CancelablePromise<DataResponse_list_PerformanceRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/top-categories",
      query: {
        limit: limit,
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
   * Top Sellers
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static topSellersApiV1DashboardTopSellersGet({
    limit = 10,
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
    limit?: number;
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
  }): CancelablePromise<DataResponse_list_PerformanceRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/top-sellers",
      query: {
        limit: limit,
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
   * Top Products
   * @returns DataResponse_list_ProductDetail__ Successful Response
   * @throws ApiError
   */
  public static topProductsApiV1DashboardTopProductsGet({
    limit = 10,
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
    limit?: number;
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
  }): CancelablePromise<DataResponse_list_ProductDetail__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/dashboard/top-products",
      query: {
        limit: limit,
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
