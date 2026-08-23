"use client";

import { RotateCcw, SlidersHorizontal } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import {
  revenueSource,
  type FilterKey,
  type Filters,
  useFilterStore,
} from "../../lib/stores/filters";
import { Button, Input, Label } from "../ui";

const queryNames: Record<FilterKey, string> = {
  dateFrom: "date_from",
  dateTo: "date_to",
  region: "region",
  state: "state",
  cityType: "city_type",
  category: "category",
  subCategory: "sub_category",
  segment: "segment",
  shipMode: "ship_mode",
  orderValueTier: "order_value_tier",
  discountBand: "discount_band",
};
const allKeys = Object.keys(queryNames) as FilterKey[];
function fieldsFor(pathname: string): FilterKey[] {
  if (
    pathname.includes("classification") ||
    pathname.includes("analytics") ||
    pathname === "/settings"
  )
    return [];
  if (pathname.includes("customers"))
    return [
      "dateFrom",
      "dateTo",
      "region",
      "state",
      "cityType",
      "segment",
      "orderValueTier",
    ];
  if (pathname.includes("products"))
    return ["dateFrom", "dateTo", "category", "subCategory", "discountBand"];
  if (pathname.includes("regional"))
    return ["dateFrom", "dateTo", "region", "state", "cityType", "shipMode"];
  if (pathname.includes("insights"))
    return ["category", "subCategory", "discountBand"];
  return [
    "dateFrom",
    "dateTo",
    "region",
    "state",
    "cityType",
    "category",
    "subCategory",
  ];
}
const labels: Record<FilterKey, string> = {
  dateFrom: "From",
  dateTo: "To",
  region: "Region",
  state: "State",
  cityType: "City type",
  category: "Category",
  subCategory: "Sub-category",
  segment: "Segment",
  shipMode: "Ship mode",
  orderValueTier: "Order-value tier",
  discountBand: "Discount band",
};

export function FilterBar() {
  const pathname = usePathname();
  const router = useRouter();
  const search = useSearchParams();
  const { filters, hydrated, hydrate, set, reset } = useFilterStore();
  const visible = fieldsFor(pathname);
  useEffect(() => {
    if (!hydrated) {
      const initial: Filters = {};
      allKeys.forEach((key) => {
        const value = search.get(queryNames[key]);
        if (value) initial[key] = value;
      });
      hydrate(initial);
    }
  }, [hydrate, hydrated, search]);
  useEffect(() => {
    if (!hydrated) return;
    const params = new URLSearchParams();
    allKeys.forEach((key) => {
      const value = filters[key];
      if (value) params.set(queryNames[key], value);
    });
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, {
      scroll: false,
    });
  }, [filters, hydrated, pathname, router]);
  if (!visible.length) return null;
  const showsRevenueRoute =
    pathname === "/dashboard" || pathname === "/dashboard/sales";
  return (
    <section
      className="border-b bg-surface/70 px-4 py-3 sm:px-6"
      aria-label="Shared dashboard filters"
    >
      <div className="mx-auto flex max-w-[1600px] items-end gap-2 overflow-x-auto">
        <span className="mb-2 mr-1 flex shrink-0 items-center gap-2 text-xs font-semibold text-muted">
          <SlidersHorizontal className="h-4 w-4" /> Filters
        </span>
        {visible.map((key) => (
          <div key={key} className="w-32 shrink-0">
            <Label htmlFor={`filter-${key}`}>{labels[key]}</Label>
            <Input
              id={`filter-${key}`}
              type={key.startsWith("date") ? "date" : "text"}
              value={filters[key] ?? ""}
              onChange={(event) => set(key, event.target.value)}
              placeholder={labels[key]}
            />
          </div>
        ))}
        <Button variant="ghost" className="mb-0 shrink-0 px-3" onClick={reset}>
          <RotateCcw className="h-4 w-4" /> Reset
        </Button>
      </div>
      {showsRevenueRoute && (
        <p className="mx-auto mt-2 max-w-[1600px] text-xs text-muted">
          Revenue trend route:{" "}
          <strong className="text-primary">{revenueSource(filters)}</strong>.
          Category and trusted-geography filters select their governed marts;
          unsupported cross-family combinations are not sent.
        </p>
      )}
    </section>
  );
}
