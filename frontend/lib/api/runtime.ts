import { OpenAPI } from "../../src/generated/api";

let accessToken: string | undefined;
export const setAccessToken = (token?: string) => {
  accessToken = token;
};
export const getAccessToken = () => accessToken;

OpenAPI.BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/api\/v1\/?$/, "") ??
  "http://localhost:8000";
OpenAPI.WITH_CREDENTIALS = true;
OpenAPI.CREDENTIALS = "include";
OpenAPI.TOKEN = async () => accessToken ?? "";
