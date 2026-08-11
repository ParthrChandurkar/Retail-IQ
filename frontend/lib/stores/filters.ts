"use client";

import { create } from "zustand";

export type FilterKey =
  | "dateFrom"
  | "dateTo"
  | "state"
  | "city"
  | "category"
  | "sellerId"
  | "paymentType"
  | "customerSegment"
  | "reviewScoreMin"
  | "reviewScoreMax";
export type Filters = Partial<Record<FilterKey, string>>;
const empty: Filters = {};
type Store = {
  filters: Filters;
  hydrated: boolean;
  set: (key: FilterKey, value: string) => void;
  reset: () => void;
  hydrate: (filters: Filters) => void;
};
export const useFilterStore = create<Store>((set) => ({
  filters: empty,
  hydrated: false,
  set: (key, value) =>
    set((state) => {
      const next = { ...state.filters };
      if (value) next[key] = value;
      else delete next[key];
      return { filters: next };
    }),
  reset: () => set({ filters: empty }),
  hydrate: (filters) => set({ filters, hydrated: true }),
}));

export const dateFilters = (f: Filters) => ({
  dateFrom: f.dateFrom,
  dateTo: f.dateTo,
});
export const revenueFilters = (f: Filters) => ({
  ...dateFilters(f),
  ...(f.category
    ? { category: f.category }
    : f.state
      ? { state: f.state, city: f.city }
      : f.sellerId
        ? { sellerId: f.sellerId }
        : {}),
});
export const revenueSource = (f: Filters) =>
  f.category
    ? "category mart"
    : f.state
      ? "regional mart"
      : f.sellerId
        ? "seller mart"
        : "daily mart";
export const categoryFilters = (f: Filters) => ({
  ...dateFilters(f),
  category: f.category,
});
export const sellerFilters = (f: Filters) => ({
  ...dateFilters(f),
  sellerId: f.sellerId,
});
export const regionFilters = (f: Filters) => ({
  ...dateFilters(f),
  state: f.state,
  city: f.city,
});
export const customerFilters = (f: Filters) => ({
  state: f.state,
  city: f.city,
  customerSegment: f.customerSegment,
});
export const reviewFilters = (f: Filters) => ({
  ...f,
  reviewScoreMin: f.reviewScoreMin ? Number(f.reviewScoreMin) : undefined,
  reviewScoreMax: f.reviewScoreMax ? Number(f.reviewScoreMax) : undefined,
});
