/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_DiscountProfitRow__ } from "../models/DataResponse_list_DiscountProfitRow__";
import type { DataResponse_list_PerformanceRow__ } from "../models/DataResponse_list_PerformanceRow__";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class ProductsService {
  /**
   * Product Performance
   * Return category/sub-category performance; Product ID is not analytical.
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static productPerformanceApiV1ProductsPerformanceGet({
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
  }): CancelablePromise<DataResponse_list_PerformanceRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/products/performance",
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
   * Product Categories
   * @returns DataResponse_list_PerformanceRow__ Successful Response
   * @throws ApiError
   */
  public static productCategoriesApiV1ProductsCategoriesGet({
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
  }): CancelablePromise<DataResponse_list_PerformanceRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/products/categories",
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
   * Discount Profit
   * @returns DataResponse_list_DiscountProfitRow__ Successful Response
   * @throws ApiError
   */
  public static discountProfitApiV1ProductsDiscountProfitGet({
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
  }): CancelablePromise<DataResponse_list_DiscountProfitRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/products/discount-profit",
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
