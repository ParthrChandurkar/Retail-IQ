/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_DistributionRow__ } from "../models/DataResponse_list_DistributionRow__";
import type { DataResponse_list_PaymentRow__ } from "../models/DataResponse_list_PaymentRow__";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class PaymentsService {
  /**
   * Method Mix
   * @returns DataResponse_list_PaymentRow__ Successful Response
   * @throws ApiError
   */
  public static methodMixApiV1PaymentsMethodMixGet({
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
  }): CancelablePromise<DataResponse_list_PaymentRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/payments/method-mix",
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
   * Installments Distribution
   * @returns DataResponse_list_DistributionRow__ Successful Response
   * @throws ApiError
   */
  public static installmentsDistributionApiV1PaymentsInstallmentsDistributionGet({
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
      url: "/api/v1/payments/installments-distribution",
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
