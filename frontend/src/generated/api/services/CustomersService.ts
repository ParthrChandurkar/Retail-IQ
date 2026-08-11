/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_CustomerRow_ } from "../models/DataResponse_CustomerRow_";
import type { DataResponse_list_DistributionRow__ } from "../models/DataResponse_list_DistributionRow__";
import type { DataResponse_list_SegmentRow__ } from "../models/DataResponse_list_SegmentRow__";
import type { DataResponse_RepeatPurchase_ } from "../models/DataResponse_RepeatPurchase_";
import type { PageResponse_CustomerRow_ } from "../models/PageResponse_CustomerRow_";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class CustomersService {
  /**
   * Segments
   * @returns DataResponse_list_SegmentRow__ Successful Response
   * @throws ApiError
   */
  public static segmentsApiV1CustomersSegmentsGet({
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
  }): CancelablePromise<DataResponse_list_SegmentRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/segments",
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
   * Rfm
   * @returns PageResponse_CustomerRow_ Successful Response
   * @throws ApiError
   */
  public static rfmApiV1CustomersRfmGet({
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
    page = 1,
    pageSize = 50,
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
    page?: number;
    pageSize?: number;
  }): CancelablePromise<PageResponse_CustomerRow_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/rfm",
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
        page: page,
        page_size: pageSize,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Clv Distribution
   * @returns DataResponse_list_DistributionRow__ Successful Response
   * @throws ApiError
   */
  public static clvDistributionApiV1CustomersClvDistributionGet({
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
  }): CancelablePromise<DataResponse_list_DistributionRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/clv-distribution",
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
   * Repeat Purchase
   * @returns DataResponse_RepeatPurchase_ Successful Response
   * @throws ApiError
   */
  public static repeatPurchaseApiV1CustomersRepeatPurchaseRateGet({
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
  }): CancelablePromise<DataResponse_RepeatPurchase_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/repeat-purchase-rate",
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
   * Customer Detail
   * @returns DataResponse_CustomerRow_ Successful Response
   * @throws ApiError
   */
  public static customerDetailApiV1CustomersCustomerUniqueIdGet({
    customerUniqueId,
  }: {
    customerUniqueId: string;
  }): CancelablePromise<DataResponse_CustomerRow_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/{customer_unique_id}",
      path: {
        customer_unique_id: customerUniqueId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
