"use client";
import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";
import { RegionsService } from "../../../../src/generated/api";
import { ChartCard, DataTable } from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { ErrorState } from "../../../../components/ui";
import {
  regionFilters,
  reviewFilters,
  useFilterStore,
} from "../../../../lib/stores/filters";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
} from "../../../../lib/utils";
const RegionMap = dynamic(
  () => import("../../../../components/maps/RegionMap"),
  {
    ssr: false,
    loading: () => (
      <div className="grid h-[28rem] place-items-center rounded-card bg-surface text-sm text-muted">
        Loading geographic view…
      </div>
    ),
  },
);
export default function RegionalPage() {
  const f = useFilterStore((s) => s.filters);
  const sales = useQuery({
    queryKey: ["region-sales", regionFilters(f)],
    queryFn: async () =>
      await RegionsService.regionSalesApiV1RegionsSalesGet(regionFilters(f)),
  });
  const geo = useQuery({
    queryKey: ["region-geo", regionFilters(f)],
    queryFn: async () =>
      await RegionsService.regionGeoApiV1RegionsGeoGet(regionFilters(f)),
  });
  const delivery = useQuery({
    queryKey: ["delivery", reviewFilters(f)],
    queryFn: async () =>
      await RegionsService.deliveryPerformanceApiV1RegionsDeliveryPerformanceGet(
        reviewFilters(f),
      ),
  });
  const failed = [sales, geo, delivery].find((q) => q.error);
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Regional intelligence"
        title="Geography & fulfillment"
        description="Delivered revenue, customer density, and delivery performance by state and city, using purchase date as the shared filter axis."
      />
      <div className="grid gap-4">
        <ChartCard
          title="Sales geography"
          description="Marker size reflects order volume; coordinates are median ZIP-prefix locations."
        >
          {geo.data && <RegionMap points={geo.data.data} />}
        </ChartCard>
        <div className="grid gap-4 xl:grid-cols-2">
          <ChartCard title="Regional sales">
            {sales.data && (
              <DataTable
                headers={["State", "City", "Revenue", "Orders", "Customers"]}
                rows={sales.data.data.map((r) => [
                  r.state,
                  r.city ?? "All",
                  formatCurrency(r.revenue),
                  formatNumber(r.order_count),
                  formatNumber(r.customer_count),
                ])}
              />
            )}
          </ChartCard>
          <ChartCard title="Delivery performance">
            {delivery.data && (
              <DataTable
                headers={["State", "City", "Orders", "Late rate", "Avg days"]}
                rows={delivery.data.data.map((r) => [
                  r.state ?? "All",
                  r.city ?? "All",
                  formatNumber(r.order_count),
                  formatPercent(r.late_rate_pct, 2),
                  r.avg_delivery_days
                    ? Number(r.avg_delivery_days).toFixed(2)
                    : "—",
                ])}
              />
            )}
          </ChartCard>
        </div>
      </div>
    </>
  );
}
