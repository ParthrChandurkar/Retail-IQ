"use client";

import type { RegionRow } from "../../src/generated/api";
import { formatCurrency, formatNumber } from "../../lib/utils";

export default function StateChoropleth({ states }: { states: RegionRow[] }) {
  const maximum = Math.max(...states.map((state) => Number(state.revenue)), 1);
  return (
    <div
      className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5"
      role="img"
      aria-label="Indian state revenue tile choropleth"
    >
      {states.map((state) => {
        const intensity = 0.12 + (Number(state.revenue) / maximum) * 0.78;
        return (
          <article
            key={state.state}
            className="min-h-36 rounded-card border p-4 text-ink"
            style={{
              background: `color-mix(in srgb, var(--chart-1) ${Math.round(intensity * 100)}%, var(--surface))`,
            }}
            title={`${state.latitude.toFixed(3)}, ${state.longitude.toFixed(3)}`}
          >
            <p className="text-xs font-semibold uppercase tracking-wide opacity-80">
              {state.region}
            </p>
            <h3 className="mt-1 font-semibold">{state.state}</h3>
            <p className="mt-5 text-sm font-semibold">
              {formatCurrency(state.revenue)}
            </p>
            <p className="mt-1 text-xs opacity-80">
              {formatNumber(state.order_count)} orders
            </p>
          </article>
        );
      })}
      <span className="sr-only">
        State coordinates are governed centroids used for state identity; this
        view uses filled state tiles and does not plot customer points.
      </span>
    </div>
  );
}
