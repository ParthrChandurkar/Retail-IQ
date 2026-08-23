/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_RegionRow__ } from "../models/DataResponse_list_RegionRow__";
import type { DataResponse_list_ShippingRow__ } from "../models/DataResponse_list_ShippingRow__";
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
  }): CancelablePromise<DataResponse_list_RegionRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/regions/sales",
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
   * Region Choropleth
   * Return state totals located only at governed state centroids.
   * @returns DataResponse_list_RegionRow__ Successful Response
   * @throws ApiError
   */
  public static regionChoroplethApiV1RegionsChoroplethGet({
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
  }): CancelablePromise<DataResponse_list_RegionRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/regions/choropleth",
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
   * Shipping Performance
   * @returns DataResponse_list_ShippingRow__ Successful Response
   * @throws ApiError
   */
  public static shippingPerformanceApiV1RegionsShippingPerformanceGet({
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
  }): CancelablePromise<DataResponse_list_ShippingRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/regions/shipping-performance",
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
