"use client";

import { useQuery } from "@tanstack/react-query";
import {
  ProductsService,
  RecommendationsService,
} from "../../../../src/generated/api";
import { ChartCard, DataTable } from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { RecommendationList } from "../../../../components/recommendations/RecommendationList";
import { ErrorState } from "../../../../components/ui";
import {
  discountFilters,
  useFilterStore,
} from "../../../../lib/stores/filters";
import {
  formatCurrency,
  formatPercent,
  titleCase,
} from "../../../../lib/utils";

export default function InsightsPage() {
  const filters = useFilterStore((state) => state.filters);
  const recommendations = useQuery({
    queryKey: ["recommendations"],
    queryFn: () =>
      RecommendationsService.recommendationsApiV1RecommendationsGet(),
  });
  const margin = useQuery({
    queryKey: ["insight-discount-profit", discountFilters(filters)],
    queryFn: () =>
      ProductsService.discountProfitApiV1ProductsDiscountProfitGet(
        discountFilters(filters),
      ),
  });
  const failed = [recommendations, margin].find((query) => query.error);
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Decision support"
        title="Insights & recommendations"
        description="Deterministic recommendations paired with auditable discount and profitability evidence."
      />
      <section className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Recommended actions</h2>
        {recommendations.data && (
          <RecommendationList recommendations={recommendations.data.data} />
        )}
      </section>
      <ChartCard
        title="Discount-margin evidence"
        description="Canonical discount bands and their observed profitability support the recommendation rules."
      >
        {margin.data && (
          <DataTable
            headers={[
              "Category",
              "Sub-category",
              "Discount band",
              "Average discount",
              "Profit margin",
              "Profit",
            ]}
            rows={margin.data.data.map((row) => [
              titleCase(row.category),
              titleCase(row.sub_category),
              titleCase(row.discount_band),
              formatPercent(row.avg_discount_pct, 2),
              formatPercent(row.avg_profit_margin_pct, 2),
              formatCurrency(row.total_profit),
            ])}
          />
        )}
      </ChartCard>
    </>
  );
}
