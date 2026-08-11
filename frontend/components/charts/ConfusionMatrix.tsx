import type { ModelMetrics } from "../../src/generated/api";
import { Card } from "../ui";
import { formatNumber, titleCase } from "../../lib/utils";

type MatrixRow = {
  actual_label: string;
  low_satisfaction: number;
  high_satisfaction: number;
};
export function ConfusionMatrix({
  matrix,
}: {
  matrix: ModelMetrics["confusion_matrix"];
}) {
  const rows = (matrix.rows ?? []) as MatrixRow[];
  return (
    <Card>
      <h2 className="font-semibold">Labeled confusion matrix</h2>
      <p className="mt-1 text-xs text-muted">
        Rows are actual; columns are predicted.
      </p>
      <div className="mt-6 grid grid-cols-[9rem_repeat(2,minmax(0,1fr))] gap-2 text-center text-sm">
        <span />
        <strong className="text-xs text-muted">Low satisfaction</strong>
        <strong className="text-xs text-muted">High satisfaction</strong>
        {rows.flatMap((row) => [
          <strong
            key={`${row.actual_label}-label`}
            className="flex items-center text-left text-xs"
          >
            {titleCase(row.actual_label)}
          </strong>,
          <div
            key={`${row.actual_label}-low`}
            className="rounded-control bg-primary/15 p-5 font-mono text-xl text-primary"
          >
            {formatNumber(row.low_satisfaction)}
          </div>,
          <div
            key={`${row.actual_label}-high`}
            className="rounded-control bg-accent/15 p-5 font-mono text-xl text-accent"
          >
            {formatNumber(row.high_satisfaction)}
          </div>,
        ])}
      </div>
    </Card>
  );
}
