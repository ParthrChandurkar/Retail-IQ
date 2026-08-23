"use client";

import { useQuery } from "@tanstack/react-query";
import { Layers3, UserRoundCheck } from "lucide-react";
import { CustomersService } from "../../../../src/generated/api";
import {
  ChartCard,
  DataTable,
  SegmentDonut,
} from "../../../../components/charts/Charts";
import { KPIGrid, KPICard } from "../../../../components/kpi/KPI";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { ErrorState } from "../../../../components/ui";
import {
  customerFilters,
  useFilterStore,
} from "../../../../lib/stores/filters";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  titleCase,
} from "../../../../lib/utils";

export default function CustomersPage() {
  const filters = useFilterStore((state) => state.filters);
  const applied = customerFilters(filters);
  const segments = useQuery({
    queryKey: [
      "segments",
      applied.segment,
      applied.cityType,
      applied.orderValueTier,
    ],
    queryFn: () =>
      CustomersService.segmentsApiV1CustomersSegmentsGet({
        segment: applied.segment,
        cityType: applied.cityType,
        orderValueTier: applied.orderValueTier,
      }),
  });
  const profiles = useQuery({
    queryKey: ["customer-profiles", applied],
    queryFn: () =>
      CustomersService.profilesApiV1CustomersProfilesGet({
        ...applied,
        page: 1,
        pageSize: 40,
      }),
  });
  const distribution = useQuery({
    queryKey: ["order-value-distribution", applied],
    queryFn: () =>
      CustomersService.orderValueDistributionApiV1CustomersOrderValueDistributionGet(
        applied,
      ),
  });
  const failed = [segments, profiles, distribution].find(
    (query) => query.error,
  );
  if (failed) return <ErrorState error={failed.error} />;
  const tierCount = distribution.data?.data.length ?? 0;
  return (
    <>
      <PageHeader
        eyebrow="Customer analytics"
        title="Cross-sectional customer profiles"
        description="One order per customer means analysis is based on segment, city type, trusted geography, order value, profit, and discount—not longitudinal behavior."
      />
      {profiles.data && (
        <KPIGrid>
          <KPICard
            label="Profiled customers"
            value={formatNumber(profiles.data.total)}
            detail="One cross-sectional profile each"
            icon={UserRoundCheck}
          />
          <KPICard
            label="Order-value tiers"
            value={formatNumber(tierCount)}
            detail="Data-derived quartiles"
            icon={Layers3}
          />
        </KPIGrid>
      )}
      <div className="grid gap-4 xl:grid-cols-2">
        {segments.data && <SegmentDonut data={segments.data.data} />}
        <ChartCard title="Order-value distribution">
          {distribution.data && (
            <DataTable
              headers={["Order-value tier", "Customers"]}
              rows={distribution.data.data.map((row) => [
                titleCase(row.bucket),
                formatNumber(row.count),
              ])}
            />
          )}
        </ChartCard>
        <ChartCard
          className="xl:col-span-2"
          title="Segment × order-value tier × city type"
        >
          {segments.data && (
            <DataTable
              headers={[
                "Segment",
                "Order-value tier",
                "City type",
                "Customers",
                "Average order value",
                "Average profit",
              ]}
              rows={segments.data.data.map((row) => [
                row.segment,
                titleCase(row.order_value_tier),
                row.city_type,
                formatNumber(row.customer_count),
                formatCurrency(row.avg_order_value),
                formatCurrency(row.avg_profit),
              ])}
            />
          )}
        </ChartCard>
        <ChartCard className="xl:col-span-2" title="Customer order profiles">
          {profiles.data && (
            <DataTable
              headers={[
                "Customer",
                "Segment",
                "City type",
                "State",
                "Order value",
                "Profit",
                "Discount",
              ]}
              rows={profiles.data.data.map((row) => [
                row.customer_id,
                row.segment,
                row.city_type,
                row.state,
                formatCurrency(row.order_value),
                formatCurrency(row.profit),
                formatPercent(row.discount_pct, 1),
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
