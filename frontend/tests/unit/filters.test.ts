import { beforeEach, describe, expect, it } from "vitest";
import {
  revenueFilters,
  revenueSource,
  useFilterStore,
} from "../../lib/stores/filters";

describe("shared-filter mart routing", () => {
  beforeEach(() => useFilterStore.getState().reset());

  it("uses the documented category-or-trusted-geography routing", () => {
    expect(revenueSource({})).toBe("daily mart");
    expect(revenueSource({ state: "Maharashtra" })).toBe(
      "trusted geography mart",
    );
    expect(revenueSource({ category: "Electronics" })).toBe(
      "category and sub-category mart",
    );
  });

  it("sends only the chosen mart's supported filter family", () => {
    expect(
      revenueFilters({
        dateFrom: "2023-01-01",
        category: "Electronics",
        subCategory: "Phones",
        state: "Maharashtra",
      }),
    ).toEqual({
      dateFrom: "2023-01-01",
      category: "Electronics",
      subCategory: "Phones",
    });
  });

  it("updates and removes filter state", () => {
    useFilterStore.getState().set("category", "Electronics");
    expect(useFilterStore.getState().filters.category).toBe("Electronics");
    useFilterStore.getState().set("category", "");
    expect(useFilterStore.getState().filters.category).toBeUndefined();
  });
});
