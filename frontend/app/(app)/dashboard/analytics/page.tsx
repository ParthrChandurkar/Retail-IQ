"use client";

import { useQuery } from "@tanstack/react-query";
import { AnalyticsService } from "../../../../src/generated/api";
import { CorrelationHeatmap } from "../../../../components/charts/CorrelationHeatmap";
import { ChartCard, DataTable } from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { Badge, ErrorState } from "../../../../components/ui";
import { formatNumber, titleCase } from "../../../../lib/utils";

type MatrixPayload = {
  fields: string[];
  correlation: Record<string, Record<string, number>>;
  observations: number;
};
type TestRow = {
  name: string;
  statistic: number;
  p_value: number;
  effect_size_name: string;
  effect_size: number;
  conclusion: string;
};
type StatRow = {
  field: string;
  mean: number;
  median: number;
  mode: number;
  std: number;
  variance: number;
  q1: number;
  q3: number;
};
type ScreenPayload = {
  field_summary: Array<{
    categorical_field: string;
    groups: number;
    max_effect_size: number;
    any_fdr_significant: boolean;
    classification: string;
  }>;
};

export default function AnalyticsPage() {
  const correlation = useQuery({
    queryKey: ["correlation"],
    queryFn: () =>
      AnalyticsService.correlationMatrixApiV1AnalyticsCorrelationMatrixGet({}),
  });
  const tests = useQuery({
    queryKey: ["hypothesis-tests"],
    queryFn: () =>
      AnalyticsService.hypothesisTestsApiV1AnalyticsHypothesisTestsGet({}),
  });
  const stats = useQuery({
    queryKey: ["descriptive-stats"],
    queryFn: () =>
      AnalyticsService.descriptiveStatsApiV1AnalyticsDescriptiveStatsGet({}),
  });
  const screen = useQuery({
    queryKey: ["broad-screen"],
    queryFn: () => AnalyticsService.broadScreenApiV1AnalyticsBroadScreenGet({}),
  });
  const failed = [correlation, tests, stats, screen].find(
    (query) => query.error,
  );
  if (failed) return <ErrorState error={failed.error} />;
  const matrix = correlation.data?.data as MatrixPayload | undefined;
  const testRows = tests.data?.data as TestRow[] | undefined;
  const statRows = stats.data?.data as StatRow[] | undefined;
  const screenData = screen.data?.data as ScreenPayload | undefined;
  return (
    <>
      <PageHeader
        eyebrow="Statistical analysis"
        title="Evidence behind the decisions"
        description="Real M3 descriptive statistics, broad categorical screening, and formal tests. Significance styling follows the p-value rather than the desired narrative."
      />
      <div className="grid gap-4">
        {matrix && (
          <CorrelationHeatmap
            fields={matrix.fields}
            matrix={matrix.correlation}
          />
        )}
        <div className="grid gap-4 xl:grid-cols-3">
          {testRows?.map((test) => {
            const significant = test.p_value < 0.05;
            return (
              <ChartCard
                key={test.name}
                title={test.name}
                description={test.conclusion}
              >
                <div className="mt-8 space-y-3">
                  <div className="flex justify-between border-b pb-3">
                    <span className="text-sm text-muted">Statistic</span>
                    <span className="font-mono">
                      {formatNumber(test.statistic, 4)}
                    </span>
                  </div>
                  <div className="flex justify-between border-b pb-3">
                    <span className="text-sm text-muted">Effect size</span>
                    <span className="font-mono">
                      {formatNumber(test.effect_size, 4)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm text-muted">p-value</span>
                    <Badge tone={significant ? "success" : "neutral"}>
                      {test.p_value < 0.0001
                        ? "< 0.0001"
                        : test.p_value.toFixed(4)}{" "}
                      · {significant ? "Significant" : "Not significant"}
                    </Badge>
                  </div>
                </div>
              </ChartCard>
            );
          })}
        </div>
        <ChartCard title="Broad categorical-vs-numeric screen">
          {screenData && (
            <DataTable
              headers={[
                "Field",
                "Groups",
                "Maximum effect",
                "FDR-significant",
                "Classification",
              ]}
              rows={screenData.field_summary.map((row) => [
                titleCase(row.categorical_field),
                row.groups,
                formatNumber(row.max_effect_size, 6),
                row.any_fdr_significant ? "Yes" : "No",
                titleCase(row.classification),
              ])}
            />
          )}
        </ChartCard>
        <ChartCard title="Descriptive statistics">
          {statRows && (
            <DataTable
              headers={[
                "Field",
                "Mean",
                "Median",
                "Mode",
                "Std dev",
                "Variance",
                "Q1",
                "Q3",
              ]}
              rows={statRows.map((row) => [
                titleCase(row.field),
                formatNumber(row.mean, 3),
                formatNumber(row.median, 3),
                formatNumber(row.mode, 3),
                formatNumber(row.std, 3),
                formatNumber(row.variance, 3),
                formatNumber(row.q1, 3),
                formatNumber(row.q3, 3),
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
