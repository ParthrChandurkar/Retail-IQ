"use client";

import { useQuery } from "@tanstack/react-query";
import {
  BadgeIndianRupee,
  Percent,
  ReceiptText,
  TrendingUp,
  Users,
  WalletCards,
} from "lucide-react";
import { DashboardService } from "../../../src/generated/api";
import {
  PerformanceBar,
  RevenueTrendChart,
} from "../../../components/charts/Charts";
import { KPIGrid, KPICard } from "../../../components/kpi/KPI";
import { Freshness, PageHeader } from "../../../components/layout/PageHeader";
import { ErrorState, Skeleton } from "../../../components/ui";
import {
  categoryFilters,
  dateFilters,
  revenueFilters,
  useFilterStore,
} from "../../../lib/stores/filters";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
} from "../../../lib/utils";

export default function DashboardPage() {
  const filters = useFilterStore((state) => state.filters);
  const summary = useQuery({
    queryKey: ["summary", dateFilters(filters)],
    queryFn: () =>
      DashboardService.summaryApiV1DashboardSummaryGet(dateFilters(filters)),
  });
  const trend = useQuery({
    queryKey: ["revenue", revenueFilters(filters)],
    queryFn: () =>
      DashboardService.revenueTrendApiV1DashboardRevenueTrendGet(
        revenueFilters(filters),
      ),
  });
  const categories = useQuery({
    queryKey: ["top-categories", categoryFilters(filters)],
    queryFn: () =>
      DashboardService.topCategoriesApiV1DashboardTopCategoriesGet({
        ...categoryFilters(filters),
        limit: 8,
      }),
  });
  if (summary.isLoading) return <DashboardSkeleton />;
  const failed = [summary, trend, categories].find((query) => query.error);
  if (failed) return <ErrorState error={failed.error} />;
  const kpi = summary.data!.data;
  return (
    <>
      <PageHeader
        eyebrow="Executive overview"
        title="Business performance"
        description="Revenue, profit, discount, demand, customers, and category performance from the governed Indian Store Data marts."
      />
      <KPIGrid>
        <KPICard
          label="Revenue"
          value={formatCurrency(kpi.total_revenue)}
          detail={`${kpi.period_start} — ${kpi.period_end}`}
          icon={BadgeIndianRupee}
        />
        <KPICard
          label="Total profit"
          value={formatCurrency(kpi.total_profit)}
          detail={`${formatPercent(kpi.profit_margin_pct, 2)} margin`}
          icon={TrendingUp}
        />
        <KPICard
          label="Orders"
          value={formatNumber(kpi.total_orders)}
          detail="All source orders"
          icon={ReceiptText}
        />
        <KPICard
          label="Customers"
          value={formatNumber(kpi.total_customers)}
          detail="Distinct customer IDs"
          icon={Users}
        />
        <KPICard
          label="Average order value"
          value={formatCurrency(kpi.average_order_value)}
          detail="Revenue ÷ distinct orders"
          icon={WalletCards}
        />
        <KPICard
          label="Average discount"
          value={formatPercent(kpi.avg_discount_pct, 2)}
          detail="Mean source discount"
          icon={Percent}
        />
      </KPIGrid>
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="xl:col-span-2">
          {trend.data && (
            <RevenueTrendChart data={trend.data.data} accessible />
          )}
        </div>
        {categories.data && (
          <PerformanceBar
            title="Category revenue"
            data={categories.data.data}
          />
        )}
      </div>
      <Freshness value={summary.data?.generated_at} />
    </>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-24" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <Skeleton key={index} className="h-32" />
        ))}
      </div>
      <Skeleton className="h-96" />
    </div>
  );
}
