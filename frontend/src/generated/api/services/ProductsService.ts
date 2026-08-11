/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_PerformanceRow__ } from "../models/DataResponse_list_PerformanceRow__";
import type { DataResponse_ProductDetail_ } from "../models/DataResponse_ProductDetail_";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class ProductsService {
  /**
   * Product Performance
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static productPerformanceApiV1ProductsPerformanceGet({
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
      url: "/api/v1/products/performance",
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
   * Product Categories
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static productCategoriesApiV1ProductsCategoriesGet({
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
      url: "/api/v1/products/categories",
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
   * Product Detail
   * @returns DataResponse_ProductDetail_ Successful Response
   * @throws ApiError
   */
  public static productDetailApiV1ProductsProductIdGet({
    productId,
  }: {
    productId: string;
  }): CancelablePromise<DataResponse_ProductDetail_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/products/{product_id}",
      path: {
        product_id: productId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
