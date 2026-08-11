/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdminSettingPayload } from "../models/AdminSettingPayload";
import type { DataResponse_AdminSettingPayload_ } from "../models/DataResponse_AdminSettingPayload_";
import type { DataResponse_RefreshStatus_ } from "../models/DataResponse_RefreshStatus_";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class AdminService {
  /**
   * Get Settings
   * @returns DataResponse_AdminSettingPayload_ Successful Response
   * @throws ApiError
   */
  public static getSettingsApiV1AdminSettingsGet(): CancelablePromise<DataResponse_AdminSettingPayload_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/admin/settings",
    });
  }
  /**
   * Put Settings
   * @returns DataResponse_AdminSettingPayload_ Successful Response
   * @throws ApiError
   */
  public static putSettingsApiV1AdminSettingsPut({
    requestBody,
  }: {
    requestBody: AdminSettingPayload;
  }): CancelablePromise<DataResponse_AdminSettingPayload_> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/admin/settings",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Data Refresh Status
   * @returns DataResponse_RefreshStatus_ Successful Response
   * @throws ApiError
   */
  public static dataRefreshStatusApiV1AdminDataRefreshStatusGet(): CancelablePromise<DataResponse_RefreshStatus_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/admin/data-refresh-status",
    });
  }
}
