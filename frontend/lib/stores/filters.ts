"use client";

import { create } from "zustand";

export type FilterKey =
  | "dateFrom"
  | "dateTo"
  | "region"
  | "state"
  | "cityType"
  | "category"
  | "subCategory"
  | "segment"
  | "shipMode"
  | "orderValueTier"
  | "discountBand";
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
    ? { category: f.category, subCategory: f.subCategory }
    : f.region || f.state || f.cityType
      ? { region: f.region, state: f.state, cityType: f.cityType }
      : {}),
});
export const revenueSource = (f: Filters) =>
  f.category
    ? "category and sub-category mart"
    : f.region || f.state || f.cityType
      ? "trusted geography mart"
      : "daily mart";
export const categoryFilters = (f: Filters) => ({
  ...dateFilters(f),
  category: f.category,
  subCategory: f.subCategory,
});
export const regionFilters = (f: Filters) => ({
  ...dateFilters(f),
  region: f.region,
  state: f.state,
  cityType: f.cityType,
});
export const customerFilters = (f: Filters) => ({
  ...dateFilters(f),
  region: f.region,
  state: f.state,
  cityType: f.cityType,
  segment: f.segment,
  orderValueTier: f.orderValueTier,
});
export const discountFilters = (f: Filters) => ({
  category: f.category,
  subCategory: f.subCategory,
  discountBand: f.discountBand,
});
export const shippingFilters = (f: Filters) => ({
  ...dateFilters(f),
  region: f.region,
  shipMode: f.shipMode,
});
