/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_PerformanceRow__ } from "../models/DataResponse_list_PerformanceRow__";
import type { DataResponse_SellerDetail_ } from "../models/DataResponse_SellerDetail_";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class SellersService {
  /**
   * Seller Performance
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static sellerPerformanceApiV1SellersPerformanceGet({
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
  }): CancelablePromise<DataResponse_list_PerformanceRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/sellers/performance",
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
   * Seller Detail
   * @returns DataResponse_SellerDetail_ Successful Response
   * @throws ApiError
   */
  public static sellerDetailApiV1SellersSellerIdGet({
    sellerId,
  }: {
    sellerId: string;
  }): CancelablePromise<DataResponse_SellerDetail_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/sellers/{seller_id}",
      path: {
        seller_id: sellerId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
