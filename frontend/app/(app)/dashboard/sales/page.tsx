"use client";
import { useQuery } from "@tanstack/react-query";
import {
  AnalyticsService,
  DashboardService,
  PaymentsService,
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
import { formatCurrency, formatNumber, titleCase } from "../../../../lib/utils";
export default function SalesPage() {
  const f = useFilterStore((s) => s.filters);
  const trend = useQuery({
    queryKey: ["sales-trend", revenueFilters(f)],
    queryFn: async () =>
      await DashboardService.revenueTrendApiV1DashboardRevenueTrendGet(
        revenueFilters(f),
      ),
  });
  const categories = useQuery({
    queryKey: ["sales-categories", categoryFilters(f)],
    queryFn: async () =>
      await DashboardService.topCategoriesApiV1DashboardTopCategoriesGet({
        ...categoryFilters(f),
        limit: 15,
      }),
  });
  const products = useQuery({
    queryKey: ["sales-products", f.dateFrom, f.dateTo, f.category, f.sellerId],
    queryFn: async () =>
      await DashboardService.topProductsApiV1DashboardTopProductsGet({
        ...dateFilters(f),
        category: f.category,
        sellerId: f.sellerId,
        limit: 15,
      }),
  });
  const season = useQuery({
    queryKey: ["seasonality", dateFilters(f)],
    queryFn: async () =>
      await AnalyticsService.seasonalityApiV1AnalyticsSeasonalityGet(
        dateFilters(f),
      ),
  });
  const payments = useQuery({
    queryKey: ["payment-mix", dateFilters(f)],
    queryFn: async () =>
      await PaymentsService.methodMixApiV1PaymentsMethodMixGet(dateFilters(f)),
  });
  const failed = [trend, categories, products, season, payments].find(
    (q) => q.error,
  );
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Sales intelligence"
        title="Revenue & demand"
        description="Purchase-date trends, category and product performance, payment behavior, and seasonality from governed revenue definitions."
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
          {season.data && (
            <DataTable
              headers={[
                "Month",
                "Average daily revenue",
                "Total revenue",
                "Orders",
              ]}
              rows={season.data.data.map((r) => [
                String(r.month_number),
                formatCurrency(String(r.average_daily_revenue)),
                formatCurrency(String(r.total_revenue)),
                formatNumber(String(r.order_count)),
              ])}
            />
          )}
        </ChartCard>
        <ChartCard title="Product performance">
          {products.data && (
            <DataTable
              headers={["Product", "Category", "Revenue", "Orders"]}
              rows={products.data.data.map((r) => [
                r.product_id.slice(0, 12),
                titleCase(r.category ?? "uncategorized"),
                formatCurrency(r.revenue),
                r.order_count,
              ])}
            />
          )}
        </ChartCard>
        <ChartCard title="Payment method mix">
          {payments.data && (
            <DataTable
              headers={["Method", "Payments", "Orders", "Value"]}
              rows={payments.data.data.map((r) => [
                titleCase(r.payment_type),
                r.payment_count,
                r.order_count,
                formatCurrency(r.payment_value),
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
