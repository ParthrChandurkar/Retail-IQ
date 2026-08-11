import type { LucideIcon } from "lucide-react";
import { Card } from "../ui";
export function KPIGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {children}
    </div>
  );
}
export function KPICard({
  label,
  value,
  detail,
  icon: Icon,
}: {
  label: string;
  value: string;
  detail?: string;
  icon?: LucideIcon;
}) {
  return (
    <Card className="transition hover:-translate-y-0.5 hover:shadow-lift">
      <div className="flex items-start justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">
          {label}
        </p>
        {Icon && <Icon className="h-4 w-4 text-primary" />}
      </div>
      <p className="mt-3 font-mono text-2xl font-semibold tracking-tight">
        {value}
      </p>
      {detail && <p className="mt-2 text-xs text-muted">{detail}</p>}
    </Card>
  );
}
