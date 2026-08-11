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
  state: "state",
  city: "city",
  category: "category",
  sellerId: "seller_id",
  paymentType: "payment_type",
  customerSegment: "customer_segment",
  reviewScoreMin: "review_score_min",
  reviewScoreMax: "review_score_max",
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
    return ["state", "city", "customerSegment"];
  if (pathname.includes("products"))
    return ["dateFrom", "dateTo", "category", "sellerId"];
  if (pathname.includes("regional"))
    return [
      "dateFrom",
      "dateTo",
      "state",
      "city",
      "category",
      "sellerId",
      "paymentType",
      "customerSegment",
      "reviewScoreMin",
      "reviewScoreMax",
    ];
  if (pathname.includes("insights"))
    return [
      "dateFrom",
      "dateTo",
      "state",
      "city",
      "category",
      "sellerId",
      "paymentType",
      "customerSegment",
      "reviewScoreMin",
      "reviewScoreMax",
    ];
  return ["dateFrom", "dateTo", "state", "city", "category", "sellerId"];
}
const labels: Record<FilterKey, string> = {
  dateFrom: "From",
  dateTo: "To",
  state: "State",
  city: "City",
  category: "Category",
  sellerId: "Seller",
  paymentType: "Payment",
  customerSegment: "Segment",
  reviewScoreMin: "Min review",
  reviewScoreMax: "Max review",
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
              type={
                key.startsWith("date")
                  ? "date"
                  : key.startsWith("review")
                    ? "number"
                    : "text"
              }
              min={key.startsWith("review") ? 1 : undefined}
              max={key.startsWith("review") ? 5 : undefined}
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
          Category takes routing priority, then geography, then seller, matching
          the mart-routing contract.
        </p>
      )}
    </section>
  );
}
