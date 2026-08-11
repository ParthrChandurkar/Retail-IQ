/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse_list_Recommendation__ } from "../models/DataResponse_list_Recommendation__";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class RecommendationsService {
  /**
   * Recommendations
   * @returns DataResponse_list_Recommendation__ Successful Response
   * @throws ApiError
   */
  public static recommendationsApiV1RecommendationsGet(): CancelablePromise<DataResponse_list_Recommendation__> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/recommendations",
    });
  }
}
