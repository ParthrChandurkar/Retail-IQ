"use client";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import type { RegionRow } from "../../src/generated/api";
import { formatCurrency, formatNumber } from "../../lib/utils";
export default function RegionMap({ points }: { points: RegionRow[] }) {
  const valid = points.filter((p) => p.latitude != null && p.longitude != null);
  return (
    <MapContainer
      center={[-14.2, -51.9]}
      zoom={4}
      scrollWheelZoom={false}
      className="h-[28rem] w-full"
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {valid.map((point) => (
        <CircleMarker
          key={`${point.state}-${point.city}`}
          center={[point.latitude!, point.longitude!]}
          radius={Math.max(4, Math.min(16, Math.sqrt(point.order_count) / 3))}
          pathOptions={{ color: "#3E8ED0", fillOpacity: 0.55 }}
        >
          <Popup>
            <strong>
              {point.city ? `${point.city}, ` : ""}
              {point.state}
            </strong>
            <br />
            {formatCurrency(point.revenue)}
            <br />
            {formatNumber(point.order_count)} orders
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
