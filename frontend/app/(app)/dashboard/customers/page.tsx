"use client";
import { useQuery } from "@tanstack/react-query";
import { Repeat2, UserRoundCheck } from "lucide-react";
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
  const f = useFilterStore((s) => s.filters);
  const p = customerFilters(f);
  const segments = useQuery({
    queryKey: ["segments", p],
    queryFn: async () =>
      await CustomersService.segmentsApiV1CustomersSegmentsGet({
        customerSegment: f.customerSegment,
      }),
  });
  const rfm = useQuery({
    queryKey: ["rfm", p],
    queryFn: async () =>
      await CustomersService.rfmApiV1CustomersRfmGet({
        ...p,
        page: 1,
        pageSize: 40,
      }),
  });
  const clv = useQuery({
    queryKey: ["clv", p],
    queryFn: async () =>
      await CustomersService.clvDistributionApiV1CustomersClvDistributionGet(p),
  });
  const repeat = useQuery({
    queryKey: ["repeat", p],
    queryFn: async () =>
      await CustomersService.repeatPurchaseApiV1CustomersRepeatPurchaseRateGet(
        p,
      ),
  });
  const failed = [segments, rfm, clv, repeat].find((q) => q.error);
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Customer analytics"
        title="Segments, RFM & value"
        description="The customer profile mart is the single source for RFM scores, rule-based segments, historical CLV, and repeat purchase behavior."
      />
      {repeat.data && (
        <KPIGrid>
          <KPICard
            label="Profiled customers"
            value={formatNumber(repeat.data.data.total_customers)}
            detail="Delivered-order customers"
            icon={UserRoundCheck}
          />
          <KPICard
            label="Repeat customers"
            value={formatNumber(repeat.data.data.repeat_customers)}
            detail={`${formatPercent(repeat.data.data.repeat_purchase_rate_pct, 2)} repeat-purchase rate`}
            icon={Repeat2}
          />
        </KPIGrid>
      )}
      <div className="grid gap-4 xl:grid-cols-2">
        {segments.data && <SegmentDonut data={segments.data.data} />}
        <ChartCard title="Historical CLV distribution">
          {clv.data && (
            <DataTable
              headers={["Decile", "Customers"]}
              rows={clv.data.data.map((r) => [r.bucket, r.count])}
            />
          )}
        </ChartCard>
        <ChartCard
          className="xl:col-span-2"
          title="Customer RFM profiles"
          description="Highest historical spend first"
        >
          {rfm.data && (
            <DataTable
              headers={[
                "Customer",
                "State",
                "Orders",
                "Spend",
                "R/F/M",
                "Segment",
              ]}
              rows={rfm.data.data.map((r) => [
                r.customer_unique_id.slice(0, 12),
                r.primary_state ?? "—",
                r.order_count,
                formatCurrency(r.total_spend),
                `${r.recency_score}/${r.frequency_score}/${r.monetary_score}`,
                titleCase(r.rfm_segment),
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
