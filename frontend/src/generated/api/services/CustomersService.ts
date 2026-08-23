/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_CustomerDetail_ } from "../models/DataResponse_CustomerDetail_";
import type { DataResponse_list_DistributionRow__ } from "../models/DataResponse_list_DistributionRow__";
import type { DataResponse_list_SegmentRow__ } from "../models/DataResponse_list_SegmentRow__";
import type { PageResponse_CustomerProfile_ } from "../models/PageResponse_CustomerProfile_";
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
  }): CancelablePromise<DataResponse_list_SegmentRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/segments",
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
   * Profiles
   * @returns PageResponse_CustomerProfile_ Successful Response
   * @throws ApiError
   */
  public static profilesApiV1CustomersProfilesGet({
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
    page = 1,
    pageSize = 50,
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
    page?: number;
    pageSize?: number;
  }): CancelablePromise<PageResponse_CustomerProfile_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/profiles",
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
        page: page,
        page_size: pageSize,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Order Value Distribution
   * @returns DataResponse_list_DistributionRow__ Successful Response
   * @throws ApiError
   */
  public static orderValueDistributionApiV1CustomersOrderValueDistributionGet({
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
  }): CancelablePromise<DataResponse_list_DistributionRow__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/order-value-distribution",
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
   * Customer Detail
   * @returns DataResponse_CustomerDetail_ Successful Response
   * @throws ApiError
   */
  public static customerDetailApiV1CustomersCustomerIdGet({
    customerId,
  }: {
    customerId: string;
  }): CancelablePromise<DataResponse_CustomerDetail_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/customers/{customer_id}",
      path: {
        customer_id: customerId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
