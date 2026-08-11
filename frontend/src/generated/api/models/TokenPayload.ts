/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserPublic } from "./UserPublic";
export type TokenPayload = {
  access_token: string;
  token_type?: string;
  expires_in: number;
  user: UserPublic;
};
