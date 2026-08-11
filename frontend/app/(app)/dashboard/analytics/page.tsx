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
  statistic?: number;
  f_statistic?: number;
  t_statistic?: number;
  p_value: number;
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
export default function AnalyticsPage() {
  const correlation = useQuery({
    queryKey: ["correlation"],
    queryFn: async () =>
      await AnalyticsService.correlationMatrixApiV1AnalyticsCorrelationMatrixGet(
        {},
      ),
  });
  const tests = useQuery({
    queryKey: ["hypothesis-tests"],
    queryFn: async () =>
      await AnalyticsService.hypothesisTestsApiV1AnalyticsHypothesisTestsGet(
        {},
      ),
  });
  const stats = useQuery({
    queryKey: ["descriptive-stats"],
    queryFn: async () =>
      await AnalyticsService.descriptiveStatsApiV1AnalyticsDescriptiveStatsGet(
        {},
      ),
  });
  const failed = [correlation, tests, stats].find((q) => q.error);
  if (failed) return <ErrorState error={failed.error} />;
  const matrix = correlation.data?.data as MatrixPayload | undefined;
  const testRows = tests.data?.data as TestRow[] | undefined;
  const statRows = stats.data?.data as StatRow[] | undefined;
  return (
    <>
      <PageHeader
        eyebrow="Statistical analysis"
        title="Evidence behind the decisions"
        description="Descriptive statistics, multivariate relationships, and formal hypothesis tests computed from curated data—not dashboard placeholders."
      />
      <div className="grid gap-4">
        {matrix && (
          <CorrelationHeatmap
            fields={matrix.fields}
            matrix={matrix.correlation}
          />
        )}
        <div className="grid gap-4 xl:grid-cols-3">
          {testRows?.map((test) => (
            <ChartCard
              key={test.name}
              title={test.name}
              description={test.conclusion}
            >
              <div className="mt-8 space-y-3">
                <div className="flex justify-between border-b pb-3">
                  <span className="text-sm text-muted">Statistic</span>
                  <span className="font-mono">
                    {formatNumber(
                      test.statistic ??
                        test.f_statistic ??
                        test.t_statistic ??
                        0,
                      4,
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted">p-value</span>
                  <Badge tone={test.p_value < 0.05 ? "success" : "neutral"}>
                    {test.p_value < 0.0001
                      ? "< 0.0001"
                      : test.p_value.toFixed(4)}
                  </Badge>
                </div>
              </div>
            </ChartCard>
          ))}
        </div>
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
              rows={statRows.map((r) => [
                titleCase(r.field),
                formatNumber(r.mean, 3),
                formatNumber(r.median, 3),
                formatNumber(r.mode, 3),
                formatNumber(r.std, 3),
                formatNumber(r.variance, 3),
                formatNumber(r.q1, 3),
                formatNumber(r.q3, 3),
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
