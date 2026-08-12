import { beforeEach, describe, expect, it } from "vitest";
import {
  revenueFilters,
  revenueSource,
  useFilterStore,
} from "../../lib/stores/filters";

describe("shared-filter mart routing", () => {
  beforeEach(() => useFilterStore.getState().reset());

  it("uses the documented category-over-region-over-seller priority", () => {
    expect(revenueSource({})).toBe("daily mart");
    expect(revenueSource({ sellerId: "s1" })).toBe("seller mart");
    expect(revenueSource({ state: "SP", sellerId: "s1" })).toBe(
      "regional mart",
    );
    expect(revenueSource({ category: "health", state: "SP" })).toBe(
      "category mart",
    );
  });

  it("sends only the chosen mart's supported filter family", () => {
    expect(
      revenueFilters({
        dateFrom: "2018-01-01",
        category: "health",
        state: "SP",
      }),
    ).toEqual({ dateFrom: "2018-01-01", category: "health" });
  });

  it("updates and removes filter state", () => {
    useFilterStore.getState().set("category", "health");
    expect(useFilterStore.getState().filters.category).toBe("health");
    useFilterStore.getState().set("category", "");
    expect(useFilterStore.getState().filters.category).toBeUndefined();
  });
});
