import { AlertTriangle, ArrowUpRight, Lightbulb } from "lucide-react";
import type { Recommendation } from "../../src/generated/api";
import { titleCase } from "../../lib/utils";
import { Badge, Card } from "../ui";
export function RecommendationList({
  recommendations,
}: {
  recommendations: Recommendation[];
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {recommendations.map((r) => (
        <Card key={r.id} className="group">
          <div className="flex items-start justify-between">
            <span className="grid h-10 w-10 place-items-center rounded-control bg-primary/10 text-primary">
              {r.severity === "high" ? <AlertTriangle /> : <Lightbulb />}
            </span>
            <Badge tone={r.severity === "high" ? "danger" : "accent"}>
              {titleCase(r.severity)}
            </Badge>
          </div>
          <h3 className="mt-5 font-semibold">{r.title}</h3>
          <p className="mt-2 text-sm leading-6 text-muted">{r.description}</p>
          <details className="mt-4">
            <summary className="cursor-pointer text-xs font-semibold text-primary">
              Supporting metric <ArrowUpRight className="inline h-3 w-3" />
            </summary>
            <pre className="mt-2 overflow-auto rounded-control bg-background p-3 text-[11px] text-muted">
              {JSON.stringify(r.supporting_metric, null, 2)}
            </pre>
          </details>
        </Card>
      ))}
    </div>
  );
}
