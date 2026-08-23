import type { ModelMetrics } from "../../src/generated/api";
import { formatNumber, titleCase } from "../../lib/utils";
import { Card } from "../ui";

type MatrixRow = {
  actual_label: string;
  high_profit_order: number;
  standard_profit_order: number;
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
        <strong className="text-xs text-muted">High-profit order</strong>
        <strong className="text-xs text-muted">Standard-profit order</strong>
        {rows.flatMap((row) => [
          <strong
            key={`${row.actual_label}-label`}
            className="flex items-center text-left text-xs"
          >
            {titleCase(row.actual_label)}
          </strong>,
          <div
            key={`${row.actual_label}-high`}
            className="rounded-control bg-primary/15 p-5 font-mono text-xl text-primary"
          >
            {formatNumber(row.high_profit_order)}
          </div>,
          <div
            key={`${row.actual_label}-standard`}
            className="rounded-control bg-accent/15 p-5 font-mono text-xl text-accent"
          >
            {formatNumber(row.standard_profit_order)}
          </div>,
        ])}
      </div>
    </Card>
  );
}
