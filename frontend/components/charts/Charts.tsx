"use client";

import { useTheme } from "next-themes";
import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import type {
  DiscountProfitRow,
  GlobalFeature,
  PerformanceRow,
  RegionRow,
  RevenuePoint,
  SegmentRow,
} from "../../src/generated/api";
import { cn, formatCurrency, formatNumber, titleCase } from "../../lib/utils";
import { Button, Card } from "../ui";

const palette = {
  light: ["#1B4F72", "#D99A2B", "#1E8A5F", "#775DA6"],
  dark: ["#65B5F6", "#F0B950", "#55D69B", "#B49BE8"],
};
function usePalette() {
  const { resolvedTheme } = useTheme();
  return palette[resolvedTheme === "dark" ? "dark" : "light"];
}
const tooltip = {
  contentStyle: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    color: "var(--text-primary)",
  },
  labelStyle: { color: "var(--text-primary)" },
};
export function ChartCard({
  title,
  description,
  children,
  table,
  className,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  table?: React.ReactNode;
  className?: string;
}) {
  const [showTable, setShowTable] = useState(false);
  return (
    <Card className={cn("min-h-[23rem]", className)}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="font-semibold">{title}</h2>
          {description && (
            <p className="mt-1 text-xs text-muted">{description}</p>
          )}
        </div>
        {table && (
          <Button
            variant="ghost"
            className="min-h-8 px-2 text-xs"
            onClick={() => setShowTable((value) => !value)}
          >
            {showTable ? "Show chart" : "Accessible table"}
          </Button>
        )}
      </div>
      {showTable ? table : children}
    </Card>
  );
}
export function RevenueTrendChart({
  data,
  accessible = false,
}: {
  data: RevenuePoint[];
  accessible?: boolean;
}) {
  const colors = usePalette();
  const table = accessible ? (
    <DataTable
      headers={["Date", "Revenue", "Orders"]}
      rows={data.map((row) => [
        row.date,
        formatCurrency(row.revenue),
        formatNumber(row.order_count),
      ])}
    />
  ) : undefined;
  return (
    <ChartCard
      title="Revenue trend"
      description="Revenue and profit by order date; category and trusted-geography filters route to their governed marts."
      table={table}
    >
      <div className="h-72" role="img" aria-label="Revenue trend line chart">
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fill: "var(--text-secondary)", fontSize: 11 }}
              minTickGap={30}
            />
            <YAxis
              tick={{ fill: "var(--text-secondary)", fontSize: 11 }}
              tickFormatter={(v: number) => `${Math.round(v / 1000)}k`}
            />
            <Tooltip
              {...tooltip}
              formatter={(v) => formatCurrency(Number(v))}
            />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke={colors[0]}
              strokeWidth={2.5}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
export function PerformanceBar({
  title,
  data,
}: {
  title: string;
  data: PerformanceRow[];
}) {
  const colors = usePalette();
  return (
    <ChartCard title={title}>
      <div className="h-72" role="img" aria-label={`${title} bar chart`}>
        <ResponsiveContainer>
          <BarChart
            data={data.slice(0, 10)}
            layout="vertical"
            margin={{ left: 12 }}
          >
            <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" />
            <XAxis type="number" hide />
            <YAxis
              dataKey="key"
              type="category"
              width={105}
              tick={{ fill: "var(--text-secondary)", fontSize: 10 }}
              tickFormatter={(v: string) => titleCase(v).slice(0, 16)}
            />
            <Tooltip
              {...tooltip}
              formatter={(v) => formatCurrency(Number(v))}
            />
            <Bar dataKey="revenue" fill={colors[0]} radius={[0, 5, 5, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
export function SegmentDonut({ data }: { data: SegmentRow[] }) {
  const colors = usePalette();
  const totals = Array.from(
    data.reduce((rows, row) => {
      rows.set(row.segment, (rows.get(row.segment) ?? 0) + row.customer_count);
      return rows;
    }, new Map<string, number>()),
    ([segment, customer_count]) => ({ segment, customer_count }),
  );
  return (
    <ChartCard title="Customer segments">
      <div
        className="h-72"
        role="img"
        aria-label="Customer segment donut chart"
      >
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={totals}
              dataKey="customer_count"
              nameKey="segment"
              innerRadius={60}
              outerRadius={95}
              paddingAngle={2}
            >
              {totals.map((row, index) => (
                <Cell key={row.segment} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip {...tooltip} formatter={(v) => formatNumber(Number(v))} />
            <Legend
              wrapperStyle={{ color: "var(--text-secondary)", fontSize: 11 }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
export function FeatureImportanceBar({ data }: { data: GlobalFeature[] }) {
  const colors = usePalette();
  return (
    <ChartCard
      title="Global feature importance"
      description="Model-level permutation importance, not a per-record explanation."
    >
      <div
        className="h-80"
        role="img"
        aria-label="Feature importance bar chart"
      >
        <ResponsiveContainer>
          <BarChart data={data.slice(0, 10)} layout="vertical">
            <XAxis type="number" hide />
            <YAxis
              dataKey="feature"
              type="category"
              width={145}
              tick={{ fill: "var(--text-secondary)", fontSize: 10 }}
              tickFormatter={titleCase}
            />
            <Tooltip {...tooltip} />
            <Bar dataKey="importance" fill={colors[1]} radius={[0, 5, 5, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
export function CityTypeComparison({ data }: { data: RegionRow[] }) {
  const colors = usePalette();
  const totals = Array.from(
    data.reduce((rows, row) => {
      if (!row.city_type) return rows;
      rows.set(
        row.city_type,
        (rows.get(row.city_type) ?? 0) + Number(row.revenue),
      );
      return rows;
    }, new Map<string, number>()),
    ([city_type, revenue]) => ({ city_type, revenue }),
  );
  return (
    <ChartCard
      title="Revenue by city type"
      description="Tier 1, Tier 2, and Village are compared as a first-class India-specific dimension."
    >
      <div
        className="h-72"
        role="img"
        aria-label="Revenue by city type bar chart"
      >
        <ResponsiveContainer>
          <BarChart data={totals}>
            <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" />
            <XAxis
              dataKey="city_type"
              tick={{ fill: "var(--text-secondary)" }}
            />
            <YAxis tick={{ fill: "var(--text-secondary)", fontSize: 10 }} />
            <Tooltip
              {...tooltip}
              formatter={(value) => formatCurrency(Number(value))}
            />
            <Bar dataKey="revenue" fill={colors[2]} radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

export function DiscountProfitChart({ data }: { data: DiscountProfitRow[] }) {
  const colors = usePalette();
  const points = data.map((row) => ({
    ...row,
    discount: Number(row.avg_discount_pct),
    margin: Number(row.avg_profit_margin_pct),
  }));
  return (
    <ChartCard
      title="Discount vs profit margin"
      description="Each point is a category, sub-category, and canonical discount-band aggregate."
    >
      <div
        className="h-72"
        role="img"
        aria-label="Discount versus profit margin scatter chart"
      >
        <ResponsiveContainer>
          <ScatterChart margin={{ bottom: 8, left: 8 }}>
            <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="discount"
              name="Average discount"
              unit="%"
              tick={{ fill: "var(--text-secondary)", fontSize: 10 }}
            />
            <YAxis
              type="number"
              dataKey="margin"
              name="Profit margin"
              unit="%"
              tick={{ fill: "var(--text-secondary)", fontSize: 10 }}
            />
            <ZAxis range={[45, 45]} />
            <Tooltip {...tooltip} cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={points} fill={colors[1]} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
export function DataTable({
  headers,
  rows,
}: {
  headers: string[];
  rows: Array<Array<string | number>>;
}) {
  return (
    <div className="max-h-80 overflow-auto">
      <table className="w-full text-left text-sm">
        <thead className="sticky top-0 bg-surface text-xs uppercase text-muted">
          <tr>
            {headers.map((h) => (
              <th key={h} className="border-b px-3 py-2">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={`${i}-${row[0]}`} className="border-b last:border-0">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-2 font-mono text-xs">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
