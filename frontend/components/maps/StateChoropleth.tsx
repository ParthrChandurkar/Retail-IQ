"use client";

import { useEffect, useMemo, useState } from "react";
import type { Feature, FeatureCollection, Geometry } from "geojson";
import type { LatLngBoundsExpression, Layer, PathOptions } from "leaflet";
import { GeoJSON, MapContainer } from "react-leaflet";
import type { RegionRow } from "../../src/generated/api";
import { formatCurrency, formatNumber } from "../../lib/utils";

type StateProperties = { ST_NM?: string };
type StateFeature = Feature<Geometry, StateProperties>;
type StateBoundaries = FeatureCollection<Geometry, StateProperties>;
type Metric = "revenue" | "profit" | "orders";

const INDIA_BOUNDS: LatLngBoundsExpression = [
  [6.5, 67.5],
  [37.5, 98],
];
const STATE_BOUNDARIES_URL = "/maps/india-states.geojson";

// India's 28 states plus Delhi, which is a data-bearing union territory in
// the source dataset. Other union territories are outside this state analysis.
export const DISPLAYED_STATE_NAMES = new Set([
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Delhi",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
]);

const metricLabels: Record<Metric, string> = {
  revenue: "Revenue",
  profit: "Profit",
  orders: "Order count",
};

function metricValue(row: RegionRow, metric: Metric) {
  if (metric === "profit") return Number(row.total_profit);
  if (metric === "orders") return row.order_count;
  return Number(row.revenue);
}

function metricDisplay(row: RegionRow, metric: Metric) {
  if (metric === "profit") return formatCurrency(row.total_profit);
  if (metric === "orders") return `${formatNumber(row.order_count)} orders`;
  return formatCurrency(row.revenue);
}

function fillFor(value: number, maximum: number) {
  const ratio = maximum <= 0 ? 0 : Math.max(0, Math.min(1, value / maximum));
  const lightness = 88 - ratio * 55;
  return `hsl(205 68% ${lightness}%)`;
}

export default function StateChoropleth({ states }: { states: RegionRow[] }) {
  const [metric, setMetric] = useState<Metric>("revenue");
  const [boundaries, setBoundaries] = useState<StateBoundaries | null>(null);
  const [boundaryError, setBoundaryError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch(STATE_BOUNDARIES_URL, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("State boundaries unavailable");
        return response.json() as Promise<StateBoundaries>;
      })
      .then((collection) => {
        setBoundaries({
          ...collection,
          features: collection.features.filter((feature) =>
            DISPLAYED_STATE_NAMES.has(feature.properties?.ST_NM ?? ""),
          ),
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        setBoundaryError(true);
      });
    return () => controller.abort();
  }, []);

  const stateData = useMemo(
    () => new Map(states.map((state) => [state.state, state])),
    [states],
  );
  const maximum = Math.max(
    ...states.map((state) => metricValue(state, metric)),
    1,
  );
  const populatedCount = [...DISPLAYED_STATE_NAMES].filter((name) =>
    stateData.has(name),
  ).length;
  const noDataCount = DISPLAYED_STATE_NAMES.size - populatedCount;

  const style = (feature?: StateFeature): PathOptions => {
    const row = stateData.get(feature?.properties?.ST_NM ?? "");
    return {
      color: row ? "#12344d" : "#77808c",
      weight: row ? 1.25 : 0.8,
      fillColor: row ? fillFor(metricValue(row, metric), maximum) : "#cbd0d6",
      fillOpacity: row ? 0.88 : 0.55,
    };
  };

  const onEachFeature = (feature: StateFeature, layer: Layer) => {
    const name = feature.properties?.ST_NM ?? "Unknown state";
    const row = stateData.get(name);
    const detail = row
      ? `<strong>${name}</strong><br>${metricLabels[metric]}: ${metricDisplay(row, metric)}<br>${formatNumber(row.order_count)} orders`
      : `<strong>${name}</strong><br>No data`;
    layer.bindTooltip(detail, { sticky: true, direction: "top" });
  };

  return (
    <div className="space-y-3">
      <div
        className="flex flex-wrap items-center justify-between gap-3"
        aria-label="Choropleth metric controls"
      >
        <div
          className="flex flex-wrap gap-2"
          role="group"
          aria-label="Map metric"
        >
          {(Object.keys(metricLabels) as Metric[]).map((option) => (
            <button
              key={option}
              type="button"
              aria-pressed={metric === option}
              onClick={() => setMetric(option)}
              className={`rounded-full border px-3 py-1.5 text-sm font-semibold transition-colors ${
                metric === option
                  ? "border-primary bg-primary text-primaryFg"
                  : "bg-surface text-ink hover:border-primary"
              }`}
            >
              {metricLabels[option]}
            </button>
          ))}
        </div>
        <p className="text-xs text-muted" aria-live="polite">
          {populatedCount} states with data · {noDataCount} states without data
        </p>
      </div>

      <div
        role="img"
        aria-label={`Geographic map of Indian states colored by ${metricLabels[metric].toLowerCase()}`}
        className="overflow-hidden rounded-card border bg-surface"
      >
        {boundaryError ? (
          <p className="p-6 text-sm text-danger" role="alert">
            Indian state boundaries could not be loaded.
          </p>
        ) : boundaries ? (
          <MapContainer
            bounds={INDIA_BOUNDS}
            boundsOptions={{ padding: [12, 12] }}
            minZoom={3}
            maxZoom={8}
            scrollWheelZoom={false}
            className="h-[32rem] w-full"
            attributionControl
          >
            <GeoJSON
              key={metric}
              data={boundaries}
              style={style}
              onEachFeature={onEachFeature}
            />
          </MapContainer>
        ) : (
          <div className="flex h-[32rem] items-center justify-center text-sm text-muted">
            Loading Indian state boundaries…
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-4 text-xs text-muted">
        <span className="inline-flex items-center gap-2">
          <span
            className="h-3 w-3 rounded-sm bg-[#287fb3]"
            aria-hidden="true"
          />
          Higher {metricLabels[metric].toLowerCase()}
        </span>
        <span className="inline-flex items-center gap-2">
          <span
            className="h-3 w-3 rounded-sm border border-[#77808c] bg-[#cbd0d6]"
            aria-hidden="true"
          />
          No data
        </span>
        <span>Boundaries: DataMeet, pinned M1 source (CC BY 4.0)</span>
      </div>
    </div>
  );
}
