"use client";

import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";
import { RegionsService } from "../../../../src/generated/api";
import {
  ChartCard,
  CityTypeComparison,
  DataTable,
} from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { ErrorState } from "../../../../components/ui";
import {
  regionFilters,
  shippingFilters,
  useFilterStore,
} from "../../../../lib/stores/filters";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
} from "../../../../lib/utils";

const StateChoropleth = dynamic(
  () => import("../../../../components/maps/StateChoropleth"),
  { ssr: false },
);

export default function RegionalPage() {
  const filters = useFilterStore((state) => state.filters);
  const geography = regionFilters(filters);
  const sales = useQuery({
    queryKey: ["region-sales", geography],
    queryFn: () => RegionsService.regionSalesApiV1RegionsSalesGet(geography),
  });
  const choropleth = useQuery({
    queryKey: ["region-choropleth", geography],
    queryFn: () =>
      RegionsService.regionChoroplethApiV1RegionsChoroplethGet(geography),
  });
  const shipping = useQuery({
    queryKey: ["shipping", shippingFilters(filters)],
    queryFn: () =>
      RegionsService.shippingPerformanceApiV1RegionsShippingPerformanceGet(
        shippingFilters(filters),
      ),
  });
  const failed = [sales, choropleth, shipping].find((query) => query.error);
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Regional intelligence"
        title="Trusted geography & shipping"
        description="State revenue uses the governed state-to-region reference. City type is shown as a first-class comparison, while shipping duration remains descriptive."
      />
      <div className="grid gap-4">
        <ChartCard
          title="Indian state choropleth"
          description="Geographic state boundaries use selectable revenue, profit, and order-count scales. States without transactions remain visible in neutral gray."
        >
          {choropleth.data && <StateChoropleth states={choropleth.data.data} />}
        </ChartCard>
        <div className="grid gap-4 xl:grid-cols-2">
          {sales.data && <CityTypeComparison data={sales.data.data} />}
          <ChartCard title="Regional sales">
            {sales.data && (
              <DataTable
                headers={[
                  "Region",
                  "State",
                  "City type",
                  "Revenue",
                  "Profit",
                  "Margin",
                ]}
                rows={sales.data.data.map((row) => [
                  row.region,
                  row.state,
                  row.city_type ?? "All",
                  formatCurrency(row.revenue),
                  formatCurrency(row.total_profit),
                  formatPercent(row.profit_margin_pct, 2),
                ])}
              />
            )}
          </ChartCard>
        </div>
        <ChartCard title="Shipping-duration description">
          {shipping.data && (
            <DataTable
              headers={[
                "Date",
                "Region",
                "Ship mode",
                "Orders",
                "Average days",
                "Median days",
                "Range",
              ]}
              rows={shipping.data.data.map((row) => [
                row.date,
                row.region,
                row.ship_mode,
                formatNumber(row.order_count),
                formatNumber(row.avg_shipping_days, 2),
                formatNumber(row.median_shipping_days, 2),
                `${row.min_shipping_days}–${row.max_shipping_days}`,
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
