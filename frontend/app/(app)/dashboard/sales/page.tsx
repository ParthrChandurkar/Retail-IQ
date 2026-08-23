"use client";

import { useQuery } from "@tanstack/react-query";
import {
  AnalyticsService,
  DashboardService,
  ProductsService,
} from "../../../../src/generated/api";
import {
  ChartCard,
  DataTable,
  PerformanceBar,
  RevenueTrendChart,
} from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { ErrorState } from "../../../../components/ui";
import {
  categoryFilters,
  dateFilters,
  revenueFilters,
  useFilterStore,
} from "../../../../lib/stores/filters";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  titleCase,
} from "../../../../lib/utils";

export default function SalesPage() {
  const filters = useFilterStore((state) => state.filters);
  const trend = useQuery({
    queryKey: ["sales-trend", revenueFilters(filters)],
    queryFn: () =>
      DashboardService.revenueTrendApiV1DashboardRevenueTrendGet(
        revenueFilters(filters),
      ),
  });
  const categories = useQuery({
    queryKey: ["sales-categories", categoryFilters(filters)],
    queryFn: () =>
      DashboardService.topCategoriesApiV1DashboardTopCategoriesGet({
        ...categoryFilters(filters),
        limit: 15,
      }),
  });
  const subCategories = useQuery({
    queryKey: ["sales-sub-categories", categoryFilters(filters)],
    queryFn: () =>
      ProductsService.productPerformanceApiV1ProductsPerformanceGet(
        categoryFilters(filters),
      ),
  });
  const seasonality = useQuery({
    queryKey: ["seasonality", dateFilters(filters)],
    queryFn: () =>
      AnalyticsService.seasonalityApiV1AnalyticsSeasonalityGet(
        dateFilters(filters),
      ),
  });
  const failed = [trend, categories, subCategories, seasonality].find(
    (query) => query.error,
  );
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Sales intelligence"
        title="Revenue, profit & demand"
        description="Order-date trends, category and sub-category performance, and five-year seasonality using the migrated metric dictionary."
      />
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="xl:col-span-2">
          {trend.data && <RevenueTrendChart data={trend.data.data} />}
        </div>
        {categories.data && (
          <PerformanceBar
            title="Category performance"
            data={categories.data.data}
          />
        )}
        <ChartCard title="Monthly seasonality">
          {seasonality.data && (
            <DataTable
              headers={[
                "Month",
                "Average daily revenue",
                "Total revenue",
                "Orders",
              ]}
              rows={seasonality.data.data.map((row) => [
                String(row.month_number),
                formatCurrency(String(row.average_daily_revenue)),
                formatCurrency(String(row.total_revenue)),
                formatNumber(String(row.order_count)),
              ])}
            />
          )}
        </ChartCard>
        <ChartCard className="xl:col-span-2" title="Sub-category performance">
          {subCategories.data && (
            <DataTable
              headers={[
                "Category / sub-category",
                "Revenue",
                "Profit",
                "Margin",
                "Orders",
              ]}
              rows={subCategories.data.data.map((row) => [
                titleCase(row.key),
                formatCurrency(row.revenue),
                formatCurrency(row.total_profit),
                formatPercent(row.profit_margin_pct, 2),
                formatNumber(row.order_count),
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
