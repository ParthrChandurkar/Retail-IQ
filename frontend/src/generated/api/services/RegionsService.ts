/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_DeliveryRow__ } from "../models/DataResponse_list_DeliveryRow__";
import type { DataResponse_list_RegionRow__ } from "../models/DataResponse_list_RegionRow__";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class RegionsService {
  /**
   * Region Sales
   * @returns DataResponse_list_RegionRow__ Successful Response
   * @throws ApiError
   */
  public static regionSalesApiV1RegionsSalesGet({
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
  }): CancelablePromise<DataResponse_list_RegionRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/regions/sales",
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
   * Region Geo
   * @returns DataResponse_list_RegionRow__ Successful Response
   * @throws ApiError
   */
  public static regionGeoApiV1RegionsGeoGet({
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
  }): CancelablePromise<DataResponse_list_RegionRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/regions/geo",
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
   * Delivery Performance
   * @returns DataResponse_list_DeliveryRow__ Successful Response
   * @throws ApiError
   */
  public static deliveryPerformanceApiV1RegionsDeliveryPerformanceGet({
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
  }): CancelablePromise<DataResponse_list_DeliveryRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/regions/delivery-performance",
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
