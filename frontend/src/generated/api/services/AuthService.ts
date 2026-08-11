/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_TokenPayload_ } from "../models/DataResponse_TokenPayload_";
import type { DataResponse_UserPublic_ } from "../models/DataResponse_UserPublic_";
import type { LoginRequest } from "../models/LoginRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class AuthService {
  /**
   * Login Route
   * @returns DataResponse_TokenPayload_ Successful Response
   * @throws ApiError
   */
  public static loginRouteApiV1AuthLoginPost({
    requestBody,
  }: {
    requestBody: LoginRequest;
  }): CancelablePromise<DataResponse_TokenPayload_> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/auth/login",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Refresh Route
   * @returns DataResponse_TokenPayload_ Successful Response
   * @throws ApiError
   */
  public static refreshRouteApiV1AuthRefreshPost({
    refreshToken,
  }: {
    refreshToken?: string | null;
  }): CancelablePromise<DataResponse_TokenPayload_> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/auth/refresh",
      cookies: {
        refresh_token: refreshToken,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Me Route
   * @returns DataResponse_UserPublic_ Successful Response
   * @throws ApiError
   */
  public static meRouteApiV1AuthMeGet(): CancelablePromise<DataResponse_UserPublic_> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/auth/me",
    });
  }
}
