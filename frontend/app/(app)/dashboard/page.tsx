"use client";
import { useQuery } from "@tanstack/react-query";
import {
  CircleDollarSign,
  PackageCheck,
  ReceiptText,
  Users,
} from "lucide-react";
import { DashboardService } from "../../../src/generated/api";
import {
  RevenueTrendChart,
  PerformanceBar,
  DataTable,
  ChartCard,
} from "../../../components/charts/Charts";
import { KPIGrid, KPICard } from "../../../components/kpi/KPI";
import { Freshness, PageHeader } from "../../../components/layout/PageHeader";
import { ErrorState, Skeleton } from "../../../components/ui";
import {
  categoryFilters,
  dateFilters,
  revenueFilters,
  sellerFilters,
  useFilterStore,
} from "../../../lib/stores/filters";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
} from "../../../lib/utils";
export default function DashboardPage() {
  const filters = useFilterStore((s) => s.filters);
  const summary = useQuery({
    queryKey: ["summary", dateFilters(filters)],
    queryFn: async () =>
      await DashboardService.summaryApiV1DashboardSummaryGet(
        dateFilters(filters),
      ),
  });
  const trend = useQuery({
    queryKey: ["revenue", revenueFilters(filters)],
    queryFn: async () =>
      await DashboardService.revenueTrendApiV1DashboardRevenueTrendGet(
        revenueFilters(filters),
      ),
  });
  const categories = useQuery({
    queryKey: ["top-categories", categoryFilters(filters)],
    queryFn: async () =>
      await DashboardService.topCategoriesApiV1DashboardTopCategoriesGet({
        ...categoryFilters(filters),
        limit: 8,
      }),
  });
  const sellers = useQuery({
    queryKey: ["top-sellers", sellerFilters(filters)],
    queryFn: async () =>
      await DashboardService.topSellersApiV1DashboardTopSellersGet({
        ...sellerFilters(filters),
        limit: 8,
      }),
  });
  const products = useQuery({
    queryKey: [
      "top-products",
      filters.dateFrom,
      filters.dateTo,
      filters.category,
      filters.sellerId,
    ],
    queryFn: async () =>
      await DashboardService.topProductsApiV1DashboardTopProductsGet({
        ...dateFilters(filters),
        category: filters.category,
        sellerId: filters.sellerId,
        limit: 8,
      }),
  });
  if (summary.isLoading) return <DashboardSkeleton />;
  if (summary.error) return <ErrorState error={summary.error} />;
  const kpi = summary.data!.data;
  return (
    <>
      <PageHeader
        eyebrow="Executive overview"
        title="Business performance"
        description="A governed view of delivered-order revenue, demand, customers, categories, products, and sellers."
      />
      <KPIGrid>
        <KPICard
          label="Revenue"
          value={formatCurrency(kpi.total_revenue)}
          detail={`${kpi.period_start} — ${kpi.period_end}`}
          icon={CircleDollarSign}
        />
        <KPICard
          label="Orders"
          value={formatNumber(kpi.total_orders)}
          detail={
            kpi.revenue_mom_growth_pct == null
              ? "Selected period"
              : `${formatPercent(kpi.revenue_mom_growth_pct)} MoM revenue`
          }
          icon={ReceiptText}
        />
        <KPICard
          label="Customers"
          value={formatNumber(kpi.total_customers)}
          detail="Distinct delivered-order customers"
          icon={Users}
        />
        <KPICard
          label="Average order value"
          value={formatCurrency(kpi.average_order_value)}
          detail="Revenue ÷ delivered orders"
          icon={PackageCheck}
        />
      </KPIGrid>
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="xl:col-span-2">
          {trend.isLoading ? (
            <Skeleton className="h-96" />
          ) : trend.error ? (
            <ErrorState error={trend.error} />
          ) : (
            <RevenueTrendChart data={trend.data!.data} accessible />
          )}
        </div>
        {categories.isLoading ? (
          <Skeleton className="h-80" />
        ) : categories.error ? (
          <ErrorState error={categories.error} />
        ) : (
          <PerformanceBar title="Top categories" data={categories.data!.data} />
        )}
        {sellers.isLoading ? (
          <Skeleton className="h-80" />
        ) : sellers.error ? (
          <ErrorState error={sellers.error} />
        ) : (
          <PerformanceBar title="Top sellers" data={sellers.data!.data} />
        )}
        <ChartCard
          title="Top products"
          description="Product-level delivered revenue"
        >
          {products.isLoading ? (
            <Skeleton className="h-64" />
          ) : products.error ? (
            <ErrorState error={products.error} />
          ) : (
            <DataTable
              headers={["Product", "Category", "Revenue", "Units"]}
              rows={products.data!.data.map((row) => [
                row.product_id.slice(0, 12),
                row.category ?? "Uncategorized",
                formatCurrency(row.revenue),
                row.units,
              ])}
            />
          )}
        </ChartCard>
      </div>
      <Freshness value={summary.data?.generated_at} />
    </>
  );
}
function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-24" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <Skeleton className="h-96" />
    </div>
  );
}
